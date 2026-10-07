# job-screener (MVP)

doda の「採用プロジェクト担当紹介求人」一覧ページ（ブラウザ保存HTML）を読み、
自分の希望条件で **A / B / C / D / ?** にトリアージして Excel に出力するツール。

> 目的は完全自動化ではなく「**選別ロジックが実用になるか**を小さく検証する」こと。
> 402件を、人間が読むべき数十件に絞り込むのが狙い。

## できること（MVP スコープ）

1. 保存済みHTML（複数可）を読み込む
2. 求人を抽出・構造化（会社名 / 求人名 / 年収 / URL / 既読 / 応募状況 など）
3. `config/criteria.yaml` のルールで採点（加点・減点・除外）
4. A/B/C/D/? に分類
5. Excel 出力（ランク色分け・URLリンク・オートフィルタ付き）

一覧ページだけでは判断できない項目（勤務地詳細・必須/歓迎条件・業務比率）は
無理に○×せず「要確認事項」列に残す。

## 判定ルール（概要）

- **最低年収 450万**：提示レンジの上限が450万未満なら除外D。レンジが450万をまたぐ場合は
  「応相談」の懸念付きで残す（上限は誇張が混じるため判定には使わない）。
- **SES/客先常駐 → 除外D**。ただし「常駐無」等の否定表現は打ち消す。
- **加点最優先**：AI活用・業務効率化・DX推進。副次でAI社内SE・自社開発・リモート等。
- しきい値：スコア ≥60→A / ≥30→B / ≥0→C / それ未満→D / 年収不明→?

条件は **すべて `config/criteria.yaml` で調整可能**（コードは触らない）。

## 使い方

```bash
pip install -e .            # または pip install beautifulsoup4 PyYAML openpyxl

# 保存HTMLを data/raw_html/ に置いて実行
python -m job_screener.cli \
    --input data/raw_html \
    --criteria config/criteria.yaml \
    --output data/output/result.xlsx
```

> `data/raw_html/` の生HTMLは **Git に入れない**（自分のログイン名やセッション
> トークンを含むため）。`.gitignore` 済み。外部共有が必要な時だけ
> `job_screener.sanitize.redact_html()` で自分の情報を落とす。

## 構成

```
src/job_screener/
  models.py       Job / Evaluation データ構造
  parse_doda.py   HTML → Job（DOM依存をここに閉じ込める）
  normalize.py    年収・勤務地のテキスト正規化（純粋関数）
  criteria.py     criteria.yaml の読み込み
  evaluate.py     採点エンジン（純粋関数・テストの中心）
  export_excel.py Excel 出力
  sanitize.py     PII/トークン除去（コミット・外部送信の境界専用）
  cli.py          パイプライン結線
config/criteria.yaml   評価条件（ここを編集してチューニング）
tests/                 pytest
```

## テスト

```bash
pytest -q
```

## 今後の拡張（MVP外）

- Stage 2：有望求人だけ詳細ページを取得して `?` を潰し再評価（`enrich` ステップ）
- 一覧ページの自動巡回（Playwright）※ログイン・規約に注意。Stage 2 の詳細取得から
- 微妙な判定（実質SESか、業務比率）に LLM を「抽出器」として併用（採点は決定的に保つ）
