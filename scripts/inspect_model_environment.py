#!/usr/bin/env python3
import importlib.metadata
import os
import platform
import socket
import sys
from pathlib import Path

print("python:",sys.version.split()[0]); print("os:",platform.platform())
for package in ("torch","vllm","transformers","huggingface-hub"):
    try: print(package+":",importlib.metadata.version(package))
    except importlib.metadata.PackageNotFoundError: print(package+": not installed")
try:
 import torch
 print("cuda_available:",torch.cuda.is_available()); print("cuda_version:",torch.version.cuda or "unavailable")
 if torch.cuda.is_available(): print("gpu:",torch.cuda.get_device_name(0)); print("gpu_memory_bytes:",torch.cuda.get_device_properties(0).total_memory)
except ImportError: print("cuda_available: unknown (torch not installed)")
print("hf_token_configured:",bool(os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_TOKEN")))
for name in ("MODEL_PRIMARY_ADAPTER_PATH","MODEL_STABLE_ADAPTER_PATH"):
 value=os.getenv(name); print(name.lower()+"_exists:",bool(value and Path(value).exists()))
for port in (8000,8001,8002):
 with socket.socket() as sock:
  try: sock.bind(("127.0.0.1",port)); available=True
  except OSError: available=False
 print(f"port_{port}_available:",available)
