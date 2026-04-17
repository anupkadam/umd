from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

ConditionType = Literal[
    "planet_in_house",
    "planet_in_sign",
    "conjunction",
    "aspect",
    "planet_condition",
    "house_lord_relation",
]


class Condition(BaseModel):
    type: ConditionType

    planet: Optional[str] = None
    house_in: Optional[List[int]] = None
    sign_in: Optional[List[str]] = None

    from_planet: Optional[str] = None
    to_planet: Optional[str] = None
    aspect_type: Optional[str] = None

    condition: Optional[str] = None

    lord_of_house: Optional[int] = None
    related_to_house: Optional[int] = None
    relation: Optional[str] = None


class WeightedRule(BaseModel):
    when: Condition
    add: Optional[float] = None
    subtract: Optional[float] = None
    reason: str


class ScoreCap(BaseModel):
    min: float = 0.0
    max: float = 1.0


class Scoring(BaseModel):
    base: float = Field(..., ge=0, le=1)
    boosters: List[WeightedRule] = []
    dampeners: List[WeightedRule] = []
    cap: ScoreCap = ScoreCap()


class InterpretationBand(BaseModel):
    min_score: float
    text: str


class Interpretation(BaseModel):
    strong: Optional[InterpretationBand] = None
    moderate: Optional[InterpretationBand] = None
    weak: Optional[InterpretationBand] = None
    absent: Dict[str, str]


class ConditionsGroup(BaseModel):
    all: List[Condition] = []
    any: List[Condition] = []
    none: List[Condition] = []


class YogaRule(BaseModel):
    id: str
    name: str
    sanskrit_name: Optional[str] = None
    chapter_ref: Optional[str] = None
    tags: List[str] = []
    prerequisites: Dict[str, List[str]] = {}
    conditions: ConditionsGroup
    scoring: Scoring
    interpretation: Interpretation
    qa_snippets: Dict[str, str] = {}


class RuleFile(BaseModel):
    version: str
    book: Dict[str, str]
    terminology_profile: str
    yogas: List[YogaRule]
