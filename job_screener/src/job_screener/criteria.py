"""criteria.yaml を読み込んで型付きの Criteria にする。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Rule:
    label: str
    weight: int
    keywords: list[str]


@dataclass
class Criteria:
    salary_min: int                       # 円に変換済み
    exclude: list[Rule]
    plus: list[Rule]
    minus: list[Rule]
    thresholds: dict[str, int]
    negation_window: int
    negation_words: list[str]
    always_unknown: list[str] = field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "Criteria":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

        def rules(section: list[dict]) -> list[Rule]:
            out = []
            for r in section or []:
                out.append(Rule(label=r["label"],
                                weight=int(r.get("weight", 0)),
                                keywords=list(r["keywords"])))
            return out

        return cls(
            salary_min=int(data["must"]["salary_min_man"]) * 10_000,
            exclude=rules(data.get("exclude")),
            plus=rules(data.get("plus")),
            minus=rules(data.get("minus")),
            thresholds=dict(data["thresholds"]),
            negation_window=int(data.get("negation_window", 4)),
            negation_words=list(data.get("negation_words", [])),
            always_unknown=list(data.get("always_unknown", [])),
        )
