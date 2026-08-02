#!/usr/bin/env python3
import json
import os
from pathlib import Path

for enabled,path_var in (("MODEL_PRIMARY_ADAPTER_ENABLED","MODEL_PRIMARY_ADAPTER_PATH"),("MODEL_STABLE_ADAPTER_ENABLED","MODEL_STABLE_ADAPTER_PATH")):
    if os.getenv(enabled,"false").lower()=="true":
        path=Path(os.environ[path_var]); config=path/"adapter_config.json"
        if not path.is_dir() or not config.is_file() or not json.loads(config.read_text()).get("base_model_name_or_path"):
            raise SystemExit(f"{enabled}=true but {path_var} is not a valid adapter")
print("Adapter configuration valid")
