"""保存済み doda 一覧HTML → Job のリスト。

DOM 構造への依存はこのモジュールに閉じ込める。doda が HTML を変えたら
直すのはここだけ。採点・出力側は Job しか知らない。
"""

from __future__ import annotations

import html as ihtml
import re
from pathlib import Path

from bs4 import BeautifulSoup

from .models import Job
from .normalize import extract_location, parse_salary

_JID = re.compile(r"jid_(\d+)")
_DAYS = re.compile(r"紹介日から\s*(\d+)")


def parse_html(html: str) -> list[Job]:
    """1ファイル分のHTML文字列から求人を抽出する。"""
    soup = BeautifulSoup(html, "html.parser")
    jobs: list[Job] = []

    for card in soup.select("div.layoutList01"):
        inner = card.select_one("div.modList01")
        classes = " ".join(inner.get("class", [])) if inner else ""

        company_el = card.select_one("span.company")
        job_el = card.select_one("span.job")
        if not (company_el and job_el):
            continue  # 求人カードでない要素はスキップ
        # 詳細リンクは会社名/求人名を囲む <a>（URLパスに依存せず取得）
        a = company_el.find_parent("a") or card.select_one("h2.title a")
        if a is None:
            continue

        title = ihtml.unescape(job_el.get_text(strip=True))
        salary_min, salary_max = parse_salary(title)

        jid_m = _JID.search(classes)
        # jid を第一キーに、無ければカードの id(message_id)を使う
        job_id = jid_m.group(1) if jid_m else (card.get("id") or a.get("href", ""))

        status_el = card.select_one("span.statusMark")
        days_m = _DAYS.search(card.get_text(" ", strip=True))

        jobs.append(Job(
            job_id=job_id,
            company=ihtml.unescape(company_el.get_text(strip=True)),
            title=title,
            url=a.get("href", ""),
            salary_min=salary_min,
            salary_max=salary_max,
            is_read="modListUnread" not in classes,
            application_status=(status_el.get_text(strip=True) if status_el else None),
            days_since=int(days_m.group(1)) if days_m else None,
            location=extract_location(title),
        ))

    return jobs


def parse_files(paths: list[str | Path]) -> list[Job]:
    """複数HTMLを読み込み、job_id で重複除去して返す。

    402件を複数ページに分けて保存する運用のため、重複除去は最初から必須。
    同じ会社の別求人は job_id が異なるので残る。
    """
    seen: dict[str, Job] = {}
    for p in paths:
        text = Path(p).read_text(encoding="utf-8", errors="replace")
        for job in parse_html(text):
            seen.setdefault(job.job_id, job)   # 先勝ち
    return list(seen.values())


def find_html_files(input_path: str | Path) -> list[Path]:
    """入力がディレクトリなら *.html を、ファイルならそれ自身を返す。"""
    p = Path(input_path)
    if p.is_dir():
        return sorted(p.glob("*.html"))
    return [p]
