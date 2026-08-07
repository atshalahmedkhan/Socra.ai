# Model Evaluation

Evaluation harnesses, result reports, and comparison artifacts for trained
Socra model versions.

## Planned contents

```text
model/evaluation/
├── harness/          # Evaluation scripts and metrics code
├── results/          # Per-version evaluation reports (git-ignored for large files)
└── README.md
```

## Status

No evaluation artifacts exist yet. The training scaffold is in
`model/training/` and the benchmark runner is in `model/benchmarks/scripts/`.
Populate this directory when the first fine-tuned adapter is ready.

## Naming convention

Each evaluation result should be named after the model version it assesses,
e.g. `socra-gemma-v1-eval.json`. Never overwrite a released version's result.
