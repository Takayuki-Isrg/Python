from pathlib import Path

from job_screener.normalize import extract_location, parse_salary
from job_screener.parse_doda import parse_files, parse_html

FIX = Path(__file__).parent / "fixtures" / "sample_list.html"


def test_parse_count_and_fields():
    jobs = parse_html(FIX.read_text(encoding="utf-8"))
    assert len(jobs) == 4
    j = jobs[0]
    assert j.company == "サンプルAI株式会社"
    assert j.job_id == "9000000001"
    assert j.salary_min == 6_000_000 and j.salary_max == 9_000_000
    assert j.is_read is False          # modListUnread あり → 未読
    assert j.location == "東京"
    assert j.days_since == 3
    assert jobs[1].is_read is True     # modListUnread なし → 既読


def test_salary_parsing():
    assert parse_salary("年収：500万円～700万円") == (5_000_000, 7_000_000)
    assert parse_salary("年収 450万円") == (4_500_000, None)
    assert parse_salary("年収の記載なし") == (None, None)


def test_location_only_when_place_like():
    assert extract_location("【港区】社内SE") == "港区"
    assert extract_location("【リーダー候補】SE") is None   # 役割は勤務地ではない
    assert extract_location("【フルリモート】エンジニア") is None


def test_dedup_by_job_id():
    jobs = parse_files([FIX, FIX])   # 同じファイルを2回 → 重複除去で4件のまま
    assert len(jobs) == 4
