from typing import Dict, List, Tuple

from app.models.rule_schema import Condition, YogaRule


def evaluate_condition(condition: Condition, chart: Dict) -> Tuple[bool, str]:
    planets = chart.get("planets", {})

    if condition.type == "planet_in_house":
        planet = condition.planet
        house_in = condition.house_in or []
        if planet not in planets:
            return False, f"{planet} missing from chart."
        actual_house = planets[planet].get("house")
        ok = actual_house in house_in
        return ok, f"{planet} house {actual_house} in {house_in}: {ok}."

    if condition.type == "planet_in_sign":
        planet = condition.planet
        sign_in = condition.sign_in or []
        if planet not in planets:
            return False, f"{planet} missing from chart."
        actual_sign = planets[planet].get("sign")
        ok = actual_sign in sign_in
        return ok, f"{planet} sign {actual_sign} in {sign_in}: {ok}."

    if condition.type == "conjunction":
        p1, p2 = condition.from_planet, condition.to_planet
        if p1 not in planets or p2 not in planets:
            return False, f"Conjunction planets missing ({p1}, {p2})."
        ok = planets[p1].get("house") == planets[p2].get("house")
        return ok, f"{p1} and {p2} conjunction by house: {ok}."

    if condition.type == "aspect":
        from_planet, to_planet = condition.from_planet, condition.to_planet
        aspects = chart.get("aspects", [])
        ok = any(
            item.get("from") == from_planet
            and item.get("to") == to_planet
            and (
                condition.aspect_type is None
                or item.get("type") == condition.aspect_type
            )
            for item in aspects
        )
        return ok, f"Aspect {from_planet}->{to_planet} ({condition.aspect_type}): {ok}."

    if condition.type == "planet_condition":
        planet = condition.planet
        tag = condition.condition
        if planet not in planets:
            return False, f"{planet} missing from chart."
        flags = planets[planet].get("conditions", [])
        ok = tag in flags
        return ok, f"{planet} condition '{tag}' present: {ok}."

    if condition.type == "house_lord_relation":
        house_lords = chart.get("house_lords", {})
        relations = chart.get("relations", [])
        source = house_lords.get(condition.lord_of_house)
        target = house_lords.get(condition.related_to_house)
        if not source or not target:
            return False, "House lords missing for relation condition."
        ok = any(
            item.get("type") == condition.relation
            and item.get("from") == source
            and item.get("to") == target
            for item in relations
        )
        return ok, f"House lord relation {source}->{target} ({condition.relation}): {ok}."

    return False, f"Unsupported condition type: {condition.type}."


def _apply_scoring(rule: YogaRule, chart: Dict, reasons: List[str]) -> float:
    score = rule.scoring.base

    for booster in rule.scoring.boosters:
        ok, why = evaluate_condition(booster.when, chart)
        if ok and booster.add:
            score += booster.add
            reasons.append(f"Booster applied (+{booster.add}): {booster.reason}")
        else:
            reasons.append(f"Booster skipped: {why}")

    for dampener in rule.scoring.dampeners:
        ok, why = evaluate_condition(dampener.when, chart)
        if ok and dampener.subtract:
            score -= dampener.subtract
            reasons.append(f"Dampener applied (-{dampener.subtract}): {dampener.reason}")
        else:
            reasons.append(f"Dampener skipped: {why}")

    score = max(rule.scoring.cap.min, min(score, rule.scoring.cap.max))
    return round(score, 4)


def _select_band(rule: YogaRule, score: float, present: bool) -> Tuple[str, str]:
    if not present:
        return "absent", rule.interpretation.absent.get("text", "No clear yoga indication.")

    bands = [
        ("strong", rule.interpretation.strong),
        ("moderate", rule.interpretation.moderate),
        ("weak", rule.interpretation.weak),
    ]

    for name, band in bands:
        if band and score >= band.min_score:
            return name, band.text

    return "weak", "Yoga is present with weak support."


def evaluate_rule(rule: YogaRule, chart: Dict, present_threshold: float = 0.3) -> Dict:
    reasons: List[str] = []

    all_results = [evaluate_condition(c, chart) for c in rule.conditions.all]
    all_ok = all(r[0] for r in all_results) if all_results else True
    reasons.extend([f"ALL: {r[1]}" for r in all_results])

    any_results = [evaluate_condition(c, chart) for c in rule.conditions.any]
    any_ok = any(r[0] for r in any_results) if any_results else True
    reasons.extend([f"ANY: {r[1]}" for r in any_results])

    none_results = [evaluate_condition(c, chart) for c in rule.conditions.none]
    none_ok = not any(r[0] for r in none_results) if none_results else True
    reasons.extend([f"NONE: {r[1]}" for r in none_results])

    core_matched = all_ok and any_ok and none_ok
    if not core_matched:
        score = 0.0
        present = False
    else:
        score = _apply_scoring(rule, chart, reasons)
        present = score >= present_threshold

    band, interpretation = _select_band(rule, score, present)

    return {
        "rule_id": rule.id,
        "name": rule.name,
        "present": present,
        "score": score,
        "band": band,
        "interpretation": interpretation,
        "reasons": reasons,
        "tags": rule.tags,
    }
