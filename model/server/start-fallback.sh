#!/bin/sh
set -eu
python3 /opt/socra/validate-adapters.py
set -- serve "${FALLBACK_BASE_MODEL_NAME:-google/gemma-3-1b-it}" --host 0.0.0.0 --port 8002 --api-key "${MODEL_FALLBACK_API_KEY:?required}" --max-model-len "${FALLBACK_VLLM_MAX_MODEL_LEN:-2048}" --gpu-memory-utilization "${FALLBACK_VLLM_GPU_MEMORY_UTILIZATION:-0.30}" --max-num-seqs "${FALLBACK_VLLM_MAX_NUM_SEQS:-1}"
[ -z "${FALLBACK_VLLM_QUANTIZATION:-}" ] || set -- "$@" --quantization "$FALLBACK_VLLM_QUANTIZATION"
[ -z "${FALLBACK_VLLM_LOAD_FORMAT:-}" ] || set -- "$@" --load-format "$FALLBACK_VLLM_LOAD_FORMAT"
if [ "${MODEL_STABLE_ADAPTER_ENABLED:-false}" = true ]; then set -- "$@" --enable-lora --lora-modules "socra-gemma-v0=${MODEL_STABLE_ADAPTER_PATH}"; else set -- "$@" --served-model-name "${MODEL_FALLBACK_NAME:-gemma-3-1b-fallback}"; fi
exec vllm "$@"
