# Model runtime environment

Observed 2026-07-19:

- Host: Windows 11 build 26200
- Runtime: Docker Desktop Linux engine (WSL2 backend)
- Python: 3.12.10
- Docker: 29.6.1
- Docker Compose: 5.3.0
- GPU: NVIDIA GeForce RTX 4060 Laptop GPU
- VRAM: 8,188 MiB
- Host driver: 592.82
- CUDA reported inside container: 13.1
- GPU passthrough command: `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi`
- GPU passthrough result: success
- Free host disk observed before downloads: 362.6 GiB

The pinned vLLM image download did not complete. A ten-minute `docker pull vllm/vllm-openai:v0.9.2` attempt timed out and a later attempt was interrupted. Docker Desktop was no longer running during the final image-state check.
