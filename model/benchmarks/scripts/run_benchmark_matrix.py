#!/usr/bin/env python3
import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", required=True)
    p.add_argument("--api-key-env", default="MODEL_PRIMARY_API_KEY")
    p.add_argument("--model", required=True)
    p.add_argument("--matrix", default="1:20,2:30,4:40")
    p.add_argument("--input-file")
    p.add_argument("--output-dir", default="benchmark-results")
    a = p.parse_args()
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    results = []

    for item in a.matrix.split(","):
        concurrency, requests = map(int, item.split(":"))
        before = set(out.glob("single-user-*.json"))
        command = [
            sys.executable, str(Path(__file__).with_name("benchmark_model.py")),
            "--base-url", a.base_url, "--api-key-env", a.api_key_env,
            "--model", a.model, "--concurrency", str(concurrency),
            "--requests", str(requests), "--output-dir", a.output_dir,
        ]
        if a.input_file:
            command.extend(["--input-file", a.input_file])
        run = subprocess.run(command, check=False)
        created = sorted(set(out.glob("single-user-*.json")) - before)
        if created:
            result = json.loads(created[-1].read_text())
        else:
            result = {"concurrency": concurrency, "requests": requests}
        result["exit_code"] = run.returncode
        results.append(result)
        if run.returncode or result.get("error_rate", 1) > 0.05:
            break

    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    (out / f"summary-{stamp}.json").write_text(json.dumps(results, indent=2))
    columns = ("concurrency", "requests", "successes", "failures", "error_rate",
               "p50_ms", "p95_ms", "p99_ms", "requests_per_second", "tokens_per_second")
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in results:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    (out / f"summary-{stamp}.md").write_text("\n".join(lines))
    return max(result["exit_code"] for result in results)


if __name__ == "__main__":
    raise SystemExit(main())
