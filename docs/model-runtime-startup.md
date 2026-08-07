# Model runtime startup

Status: **blocked**

`HF_TOKEN` and `HUGGING_FACE_TOKEN` are empty. Therefore Gemma metadata access, license acceptance, checkpoint download, vLLM startup, and live endpoint verification were not possible. `model/benchmarks/scripts/verify_model_runtime.py` recorded `MISSING_TOKEN` plus connection failures for model and API endpoints.

The intended local command is:

```powershell
docker compose -f docker-compose.yml -f docker-compose.gpu.yml -f docker-compose.local.yml up --build model-primary
```

The local override binds only `127.0.0.1:8001`; the production Compose file publishes no model port.

For a remote Linux GPU host with sufficient VRAM:

```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build -d model-primary api
```

Supply `.env` through a secret-management process. Do not copy it into an image or repository.
