"""採点エンジン。副作用なしの純粋関数（ここがチューニングの速さを決める）。

判定順序:
  1. 除外キーワード(SES等) → D
  2. 年収レンジ全体が下限未満 → D
  3. 年収がまったく不明 → ?（唯一チェックできる必須条件すら確認できない）
  4. それ以外は 加点 + 減点 + 年収ペナルティ を合計し、閾値でランク化
"""

from __future__ import annotations

from .criteria import Criteria, Rule
from .models import Evaluation, Job

_STRADDLE_PENALTY = -5   # 年収レンジが下限をまたぐ時の軽い減点


def _hit(text: str, keyword: str, window: int, neg_words: list[str]) -> bool:
    """keyword が「打ち消されずに」1回以上出現するか。

    例:「1人常駐無」→ 常駐 の直後に『無』があるので打ち消し扱い。
    """
    k = len(keyword)
    start = 0
    while True:
        i = text.find(keyword, start)
        if i < 0:
            return False
        after = text[i + k: i + k + window]
        if not any(nw in after for nw in neg_words):
            return True
        start = i + k


def _fire(rules: list[Rule], text: str, crit: Criteria) -> list[Rule]:
    """発火したルールを返す（1ルール内はキーワードのいずれかが一致で発火）。"""
    out = []
    for r in rules:
        if any(_hit(text, kw, crit.negation_window, crit.negation_words)
               for kw in r.keywords):
            out.append(r)
    return out


def _fmt(rule: Rule) -> str:
    sign = "+" if rule.weight >= 0 else ""
    return f"{rule.label}({sign}{rule.weight})"


def evaluate(job: Job, crit: Criteria) -> Evaluation:
    text = job.raw_text
    unknowns = list(crit.always_unknown)

    pluses = _fire(crit.plus, text, crit)
    minuses = _fire(crit.minus, text, crit)
    excludes = _fire(crit.exclude, text, crit)

    plus_labels = [_fmt(r) for r in pluses]
    concern_labels = [_fmt(r) for r in minuses]

    score = sum(r.weight for r in pluses) + sum(r.weight for r in minuses)

    # --- 年収判定（上限は信用せず、レンジと下限で判断）---
    floor = crit.salary_min
    salary_below = False
    salary_unknown = False
    if job.salary_max is not None and job.salary_max < floor:
        salary_below = True
        concern_labels.append(f"年収上限が{floor // 10000}万未満")
    elif job.salary_min is not None and job.salary_min < floor:
        # レンジが下限をまたぐ（上限は floor 以上 or 不明）→ 残すが軽く減点
        concern_labels.append(f"年収下限が{floor // 10000}万未満(応相談)")
        score += _STRADDLE_PENALTY
    elif job.salary_min is None and job.salary_max is None:
        salary_unknown = True
        unknowns.insert(0, "年収（一覧に記載なし・要確認）")

    # --- 除外キーワード ---
    if excludes:
        concern_labels = [f"{_fmt(r)}=除外" for r in excludes] + concern_labels

    # --- ランク決定 ---
    if excludes or salary_below:
        rank = "D"
    elif salary_unknown:
        rank = "?"
    else:
        t = crit.thresholds
        if score >= t["A"]:
            rank = "A"
        elif score >= t["B"]:
            rank = "B"
        elif score >= t["C"]:
            rank = "C"
        else:
            rank = "D"

    return Evaluation(
        rank=rank,
        score=score,
        pluses=plus_labels,
        concerns=concern_labels,
        unknowns=unknowns,
    )
