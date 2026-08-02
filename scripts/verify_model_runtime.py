#!/usr/bin/env python3
import argparse
import datetime
import json
import os
from pathlib import Path

import httpx

p = argparse.ArgumentParser()
p.add_argument("--model-url", default="http://127.0.0.1:8001")
p.add_argument("--api-url", default="http://127.0.0.1:8000")
p.add_argument("--model", default="gemma-3-4b-base")
p.add_argument("--output-dir", default="test-results")
a = p.parse_args()
checks = []


def record(name, passed, detail):
    checks.append({"name": name, "passed": passed, "detail": detail})


record("HF_TOKEN", bool(os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_TOKEN")),
       "configured" if os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_TOKEN") else "MISSING_TOKEN")
key = os.getenv("MODEL_PRIMARY_API_KEY")
try:
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    with httpx.Client(timeout=5, headers=headers) as client:
        health = client.get(a.model_url + "/health")
        record("model_health", health.status_code == 200, f"HTTP {health.status_code}")
        models = client.get(a.model_url + "/v1/models")
        loaded = a.model in [item.get("id") for item in models.json().get("data", [])]
        record("model_listing", models.status_code == 200 and loaded, f"HTTP {models.status_code}; loaded={loaded}")
except Exception as exc:
    record("model_endpoints", False, type(exc).__name__)
try:
    with httpx.Client(timeout=5) as client:
        live = client.get(a.api_url + "/health/live")
        ready = client.get(a.api_url + "/health/ready")
        record("api_live", live.status_code == 200, f"HTTP {live.status_code}")
        record("api_ready", ready.status_code == 200 and ready.json().get("status") in ("ready", "degraded"),
               f"HTTP {ready.status_code}")
except Exception as exc:
    record("api_endpoints", False, type(exc).__name__)

out = Path(a.output_dir)
out.mkdir(parents=True, exist_ok=True)
report = {"timestamp": datetime.datetime.now(datetime.UTC).isoformat(), "checks": checks,
          "passed": all(check["passed"] for check in checks)}
(out / "model-runtime-verification.json").write_text(json.dumps(report, indent=2))
(out / "model-runtime-verification.md").write_text(
    "\n".join(f"- {check['name']}: {'PASS' if check['passed'] else 'FAIL'} ({check['detail']})" for check in checks)
)
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["passed"] else 1)
