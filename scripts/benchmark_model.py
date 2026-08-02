#!/usr/bin/env python3
import argparse
import asyncio
import datetime
import json
import math
import os
import statistics
from pathlib import Path

import httpx


def percentile(values, fraction):
    return sorted(values)[min(len(values) - 1, math.ceil(fraction * len(values)) - 1)] if values else None


async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", required=True)
    p.add_argument("--api-key-env", default="MODEL_PRIMARY_API_KEY")
    p.add_argument("--model", required=True)
    p.add_argument("--requests", type=int, default=20)
    p.add_argument("--concurrency", type=int, default=1)
    p.add_argument("--input-file")
    p.add_argument("--output-dir", default="benchmark-results")
    p.add_argument("--warmup-requests", type=int, default=5)
    p.add_argument("--max-output-tokens", type=int, default=128)
    a = p.parse_args()
    key = os.getenv(a.api_key_env)
    if not key:
        raise SystemExit(f"{a.api_key_env} is not configured")
    prompts = ["Ask one concise guiding question about tree traversal."]
    if a.input_file:
        prompts = [json.loads(line)["prompt"] for line in Path(a.input_file).read_text().splitlines() if line.strip()]
    semaphore = asyncio.Semaphore(a.concurrency)
    latencies, failures = [], []
    prompt_tokens = completion_tokens = total_tokens = 0
    counter = 0
    async with httpx.AsyncClient(timeout=35, headers={"Authorization": f"Bearer {key}"}) as client:
        async def one(measured=True):
            nonlocal prompt_tokens, completion_tokens, total_tokens, counter
            prompt = prompts[counter % len(prompts)]
            counter += 1
            async with semaphore:
                started = asyncio.get_running_loop().time()
                try:
                    response = await client.post(
                        a.base_url.rstrip("/") + "/v1/chat/completions",
                        json={"model": a.model, "messages": [{"role": "user", "content": prompt}],
                              "max_tokens": a.max_output_tokens},
                    )
                    response.raise_for_status()
                    data = response.json()
                    if not data["choices"][0]["message"]["content"].strip():
                        raise ValueError("empty response")
                    if measured:
                        latencies.append((asyncio.get_running_loop().time() - started) * 1000)
                        usage = data.get("usage") or {}
                        prompt_tokens += usage.get("prompt_tokens", 0)
                        completion_tokens += usage.get("completion_tokens", 0)
                        total_tokens += usage.get("total_tokens", 0)
                except Exception as exc:
                    if measured:
                        failures.append(type(exc).__name__)
        for _ in range(a.warmup_requests):
            await one(False)
        started = asyncio.get_running_loop().time()
        await asyncio.gather(*(one() for _ in range(a.requests)))
        elapsed = asyncio.get_running_loop().time() - started
    report = {
        "model": a.model, "concurrency": a.concurrency, "requests": a.requests,
        "successes": len(latencies), "failures": len(failures),
        "error_rate": len(failures) / a.requests, "elapsed_seconds": elapsed,
        "requests_per_second": len(latencies) / elapsed, "p50_ms": percentile(latencies, .5),
        "p95_ms": percentile(latencies, .95), "p99_ms": percentile(latencies, .99),
        "min_ms": min(latencies, default=None), "max_ms": max(latencies, default=None),
        "mean_ms": statistics.mean(latencies) if latencies else None,
        "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "tokens_per_second": completion_tokens / elapsed if completion_tokens else None,
    }
    out = Path(a.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%SZ")
    stem = out / f"single-user-{stamp}"
    stem.with_suffix(".json").write_text(json.dumps(report, indent=2))
    stem.with_suffix(".md").write_text("\n".join(f"- {k}: {v}" for k, v in report.items()))
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if not failures else 1)


asyncio.run(main())
