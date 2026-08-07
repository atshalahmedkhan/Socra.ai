# Annotated Data

Canonical location for all datasets used in Socra model development.

```text
annotated-data/
├── raw/          # Source data before any cleaning or annotation
├── processed/    # Cleaned, de-identified, and formatted data
├── train/        # Training split for QLoRA / SFT
├── validation/   # Validation split used during training
├── test/         # Held-out evaluation split
└── README.md
```

## Data rules

- **Never commit real student data.** Use synthetic or de-identified data only.
- All files in `raw/`, `processed/`, `train/`, `validation/`, and `test/` are
  git-ignored by default. Add a `.gitkeep` only if a directory must remain
  visible in the repository without data.
- Training data referenced by `model/training/configs/qlora.yaml` goes in
  `train/` and `validation/`. The config paths (`data/train.jsonl`,
  `data/eval.jsonl`) are relative to the training script; update them to point
  here when running locally or on Colab.
- Benchmark prompt fixtures (not training data) live in
  `model/benchmarks/prompts/`.

## Status

No datasets exist in this repository yet. This directory is a placeholder for
the data pipeline that will be built in Phase 2.
