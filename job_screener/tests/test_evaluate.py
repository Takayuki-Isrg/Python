from pathlib import Path

from job_screener.criteria import Criteria
from job_screener.evaluate import evaluate
from job_screener.models import Job

CRIT = Criteria.from_yaml(
    Path(__file__).resolve().parents[1] / "config" / "criteria.yaml"
)


def _job(title, smin=None, smax=None):
    return Job(job_id="x", company="c", title=title, url="u",
               salary_min=smin, salary_max=smax)


def test_ai_dx_job_is_high_rank():
    ev = evaluate(_job("社内SE◆AI活用／DX推進／業務効率化", 6_000_000, 9_000_000), CRIT)
    # AI40 + 業務効率化35 + DX35 + 社内SE25 = 135 → A
    assert ev.rank == "A"
    assert ev.score >= CRIT.thresholds["A"]
    assert any("AI活用" in p for p in ev.pluses)


def test_ses_is_excluded_D():
    ev = evaluate(_job("開発エンジニア◆客先常駐　年収：500万円～700万円", 5_000_000, 7_000_000), CRIT)
    assert ev.rank == "D"
    assert any("除外" in c for c in ev.concerns)


def test_negation_cancels_ses_keyword():
    # 「常駐無」は SES と判定しない（否定の打ち消し）
    ev = evaluate(_job("SE◆1人常駐無／自社サービス開発", 5_000_000, 6_000_000), CRIT)
    assert ev.rank != "D" or not any("SES" in c for c in ev.concerns)
    assert all("SES" not in c for c in ev.concerns)


def test_salary_whole_band_below_floor_is_D():
    ev = evaluate(_job("SE 年収：300万円～420万円", 3_000_000, 4_200_000), CRIT)
    assert ev.rank == "D"
    assert any("年収上限" in c for c in ev.concerns)


def test_salary_straddle_is_kept_with_concern():
    # 350〜840万: 下限は450未満だが上限は上 → 除外せず懸念付き
    ev = evaluate(_job("システム開発 年収：350万円～840万円", 3_500_000, 8_400_000), CRIT)
    assert ev.rank != "D" or ev.score > -100   # 少なくとも年収で即Dにはしない
    assert any("応相談" in c for c in ev.concerns)


def test_unknown_salary_is_question_mark():
    ev = evaluate(_job("Webエンジニア（オープンポジション）／リモート中心"), CRIT)
    assert ev.rank == "?"
    assert any("年収" in u for u in ev.unknowns)


def test_always_unknown_attached():
    ev = evaluate(_job("社内SE AI活用", 6_000_000, 8_000_000), CRIT)
    assert any("業務比率" in u for u in ev.unknowns)
