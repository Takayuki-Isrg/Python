"""保存HTMLから『自分のPII・セッション情報』を落とす（境界専用）。

パイプライン本体では使わない。使うのは2箇所だけ:
  - テスト用フィクスチャをコミットする時
  - （将来）本文を外部LLM APIに送る直前
会社名・求人情報は残す（それが成果物のため）。マスク対象はあくまで自分の情報。
"""

from __future__ import annotations

import re

_PATTERNS = [
    # ログイン名:  <p class="loginName">石動 孝幸 さん</p>
    (re.compile(r'(<p[^>]*class="loginName"[^>]*>).*?(</p>)', re.S), r"\1REDACTED\2"),
    # CSRF/セッション token hidden input
    (re.compile(r'(id="token"[^>]*value=")[^"]*(")'), r"\1REDACTED\2"),
    (re.compile(r'(name="token"[^>]*value=")[^"]*(")'), r"\1REDACTED\2"),
    # トラッキング cid/sid/token（\x3d = URLエンコードされた '='）
    (re.compile(r'((?:cid|sid|token)(?:\\x3d|=))[0-9a-fA-F]{6,}'), r"\1REDACTED"),
]


def redact_html(raw: str) -> str:
    for pat, repl in _PATTERNS:
        raw = pat.sub(repl, raw)
    return raw
