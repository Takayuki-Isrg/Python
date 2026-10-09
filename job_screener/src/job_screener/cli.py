"""コマンドライン入口。保存HTML → 抽出 → 採点 → Excel。

使い方:
  python -m job_screener.cli \
      --input data/raw_html \
      --criteria config/criteria.yaml \
      --output data/output/result.xlsx
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .criteria import Criteria
from .evaluate import evaluate
from .export_excel import export
from .parse_doda import find_html_files, parse_files

_DEFAULT_CRITERIA = Path(__file__).resolve().parents[2] / "config" / "criteria.yaml"


def run(input_path: str, criteria_path: str, output_path: str) -> None:
    files = find_html_files(input_path)
    if not files:
        raise SystemExit(f"HTMLが見つかりません: {input_path}")

    jobs = parse_files(files)
    crit = Criteria.from_yaml(criteria_path)
    results = [(job, evaluate(job, crit)) for job in jobs]

    out = export(results, output_path)

    counts = Counter(ev.rank for _, ev in results)
    print(f"読み込み: {len(files)}ファイル / 求人 {len(jobs)}件（重複除去後）")
    print("  " + "  ".join(f"{r}:{counts.get(r, 0)}" for r in ("A", "B", "C", "D", "?")))
    print(f"出力: {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description="doda求人トリアージツール (MVP)")
    ap.add_argument("--input", default="data/raw_html",
                    help="保存HTMLのディレクトリ or ファイル")
    ap.add_argument("--criteria", default=str(_DEFAULT_CRITERIA),
                    help="評価条件YAML")
    ap.add_argument("--output", default="data/output/result.xlsx",
                    help="出力Excelパス")
    args = ap.parse_args()
    run(args.input, args.criteria, args.output)


if __name__ == "__main__":
    main()
