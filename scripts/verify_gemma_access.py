#!/usr/bin/env python3
import argparse
import os
import sys

p=argparse.ArgumentParser(); p.add_argument("--download-model",action="store_true"); p.add_argument("--cache-dir",default=os.getenv("HF_HOME")); a=p.parse_args()
token=os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_TOKEN")
if not token: raise SystemExit("Set HF_TOKEN after accepting Gemma terms.")
try:
 from huggingface_hub import HfApi, snapshot_download
 model=os.getenv("BASE_MODEL_NAME","google/gemma-3-4b-it"); HfApi(token=token).model_info(model)
 snapshot_download(model,token=token,cache_dir=a.cache_dir,allow_patterns=None if a.download_model else ["config.json","tokenizer*","generation_config.json"])
 print(f"Access verified for {model}; full_download={a.download_model}")
except Exception as exc:
 print(f"Gemma access failed: {type(exc).__name__}: {exc}",file=sys.stderr); raise SystemExit(2)
