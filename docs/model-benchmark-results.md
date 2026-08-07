# Model benchmark results

No model benchmark was run. The host has an RTX 4060 Laptop GPU with 8,188 MiB and Docker GPU passthrough works, but the pinned vLLM image download did not complete, `HF_TOKEN` is missing, Gemma access was not established, and no adapter exists. No metrics are fabricated.

Later run:

```bash
python model/benchmarks/scripts/benchmark_model.py --base-url URL --model gemma-3-4b-base --requests 20 --concurrency 1
python model/benchmarks/scripts/run_benchmark_matrix.py --base-url URL --model gemma-3-4b-base
```

Targets: health p95 <500 ms, complete response p50 <8 s/p95 <20 s, error rate <1%. TTFT is not measured without streaming.
