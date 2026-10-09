"""求人の構造化データモデル。

一覧ページから「取れた事実」と「取れなかった(=要確認)」を型で区別することが目的。
取れていない項目を空文字で埋めると `?` 判定ができなくなるため、未取得は None で表す。
  - None           : まだ取得していない / 一覧からは判断できない
  - "" や []       : 取得したが該当なし
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Job:
    """1件の求人。一覧ページから抽出した段階のデータ。"""

    # --- 一覧から確実に取れるもの ---
    job_id: str                       # doda の jid。重複除去キー
    company: str
    title: str                        # span.job 全文（=キーワード判定の素材）
    url: str
    source: str = "doda"
    salary_min: int | None = None     # 円。フィルタに使う下限
    salary_max: int | None = None     # 円。表示用。誇張が混じるため判定には使わない
    is_read: bool | None = None
    application_status: str | None = None   # 「応募判断前」等
    days_since: int | None = None     # 紹介日から N 日経過

    # --- 詳細ページでしか取れない項目（MVPでは常に None） ---
    location: str | None = None       # 地名が確定できた時だけ入る
    must_requirements: str | None = None
    welcome_requirements: str | None = None
    description: str | None = None

    @property
    def raw_text(self) -> str:
        """キーワード判定に使う素材テキスト。

        詳細を取得したら description 等も連結され、同じ採点ロジックがそのまま効く。
        """
        parts = [self.title, self.description, self.must_requirements,
                 self.welcome_requirements]
        return " ".join(p for p in parts if p)


RANKS = ("A", "B", "C", "D", "?")


@dataclass
class Evaluation:
    """採点結果。『なぜそのランクか』を必ず残す（チューニングの生命線）。"""

    rank: str                              # A/B/C/D/?
    score: int
    pluses: list[str] = field(default_factory=list)    # 例「AI活用(+40)」
    concerns: list[str] = field(default_factory=list)  # 例「SES/客先常駐(除外)」
    unknowns: list[str] = field(default_factory=list)  # 例「勤務地要確認」= Stage2 で見る点
