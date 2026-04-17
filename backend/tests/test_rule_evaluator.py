from app.services.rule_evaluator import evaluate_condition, evaluate_rule
from app.services.rule_loader import load_rules


def _sample_chart():
    return {
        "planets": {
            "Sun": {"house": 5, "sign": "Aries", "conditions": ["exalted"]},
            "Mars": {"house": 10, "sign": "Capricorn", "conditions": []},
            "Jupiter": {"house": 1, "sign": "Aries", "conditions": []},
            "Venus": {"house": 3, "sign": "Gemini", "conditions": []},
        },
        "aspects": [
            {"from": "Jupiter", "to": "Sun", "type": "vedic_full"},
        ],
        "house_lords": {9: "Jupiter", 10: "Saturn"},
        "relations": [
            {"from": "Jupiter", "to": "Saturn", "type": "conjunction"},
        ],
    }


def test_condition_planet_in_house():
    from app.models.rule_schema import Condition

    ok, _ = evaluate_condition(
        Condition(type="planet_in_house", planet="Sun", house_in=[1, 5, 9]),
        _sample_chart(),
    )
    assert ok


def test_condition_aspect():
    from app.models.rule_schema import Condition

    ok, _ = evaluate_condition(
        Condition(
            type="aspect",
            from_planet="Jupiter",
            to_planet="Sun",
            aspect_type="vedic_full",
        ),
        _sample_chart(),
    )
    assert ok


def test_condition_planet_condition_false():
    from app.models.rule_schema import Condition

    ok, _ = evaluate_condition(
        Condition(type="planet_condition", planet="Mars", condition="combust"),
        _sample_chart(),
    )
    assert not ok


def test_condition_house_lord_relation():
    from app.models.rule_schema import Condition

    ok, _ = evaluate_condition(
        Condition(
            type="house_lord_relation",
            lord_of_house=9,
            related_to_house=10,
            relation="conjunction",
        ),
        _sample_chart(),
    )
    assert ok


def test_evaluate_rule_from_yaml():
    rule_file = load_rules("backend/app/rules/yoga_rules_v1.yaml")
    result = evaluate_rule(rule_file.yogas[0], _sample_chart())

    assert result["present"] is True
    assert result["score"] >= 0.75
    assert result["band"] in {"strong", "moderate"}
