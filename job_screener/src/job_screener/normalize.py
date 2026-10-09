"""求人テキストの正規化ヘルパー（DOM に依存しない純粋関数）。

doda の一覧では年収・勤務地が求人タイトル文字列の中に埋まっているため、
文字列から構造化値を取り出す責務をここに集約する。
"""

from __future__ import annotations

import re

_MAN = 10_000

# 「年収：500万円～700万円」/「年収 500万〜700万円」などに対応
_SALARY_RANGE = re.compile(
    r"年収[\s:：]*([\d,]+)\s*万円?\s*[～~〜\-ー]\s*([\d,]+)\s*万円"
)
_SALARY_SINGLE = re.compile(r"年収[\s:：]*([\d,]+)\s*万円")

# 勤務地判定。【】はキャッチコピー枠で地名とは限らないため、
#   (1) 役割・働き方など明らかに地名でない語を含めば除外
#   (2) 都道府県区市町村マーカー、または主要地名を含めば採用
# という保守的な二段構え。取りこぼしは location=None（=要確認）に落ちるだけで安全。
_PLACE_MARK = re.compile(r"[都道府県区市町村]")
_LEAD_BRACKET = re.compile(r"^\s*【([^】]+)】")
_NON_PLACE = ("候補", "面接", "未経験", "歓迎", "上場", "リモート", "在宅",
              "フレックス", "急募", "社内SE", "エンジニア", "第二新卒", "残業", "年休")
_PLACE_WORDS = ("東京", "新宿", "渋谷", "品川", "池袋", "赤坂", "天王洲", "麹町",
                "横浜", "大宮", "さいたま", "大阪", "名古屋", "福岡", "札幌", "仙台")


def parse_salary(text: str | None) -> tuple[int | None, int | None]:
    """タイトル文字列から (下限, 上限) を円で返す。取れなければ (None, None)。"""
    if not text:
        return (None, None)
    m = _SALARY_RANGE.search(text)
    if m:
        lo = int(m.group(1).replace(",", "")) * _MAN
        hi = int(m.group(2).replace(",", "")) * _MAN
        return (lo, hi)
    m = _SALARY_SINGLE.search(text)
    if m:
        return (int(m.group(1).replace(",", "")) * _MAN, None)
    return (None, None)


def extract_location(text: str | None) -> str | None:
    """先頭の【…】が地名らしければ勤務地として返す。そうでなければ None。

    doda の【】はキャッチコピー枠で、地名('港区')のことも
    役割('リーダー候補')・働き方('フルリモート')のこともあるため、
    地名マーカーを含むものだけ採用する（過検出より取りこぼしを選ぶ）。
    """
    if not text:
        return None
    m = _LEAD_BRACKET.match(text)
    if not m:
        return None
    inner = m.group(1).strip()
    if any(w in inner for w in _NON_PLACE):
        return None
    if _PLACE_MARK.search(inner) or any(w in inner for w in _PLACE_WORDS):
        return inner
    return None
