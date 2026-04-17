from pathlib import Path
from typing import Union

import yaml

from app.models.rule_schema import RuleFile


def load_rules(path: Union[str, Path]) -> RuleFile:
    """Load and validate a yoga-rule YAML file."""
    rule_path = Path(path)
    data = yaml.safe_load(rule_path.read_text(encoding="utf-8"))
    return RuleFile.model_validate(data)
