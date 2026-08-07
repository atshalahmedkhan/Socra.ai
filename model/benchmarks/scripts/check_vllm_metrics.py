#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

import httpx

p=argparse.ArgumentParser(); p.add_argument("--base-url",required=True); p.add_argument("--output",default="docs/vllm-metrics-sample.txt"); a=p.parse_args(); r=httpx.get(a.base_url.rstrip("/")+"/metrics",timeout=10); r.raise_for_status(); assert "text/plain" in r.headers.get("content-type",""); names=sorted(set(re.findall(r"^(vllm_[A-Za-z0-9_:]+)",r.text,re.MULTILINE))); Path(a.output).write_text(r.text); print("\n".join(n for n in names if any(x in n for x in ("request","token","queue","running","cache"))))
