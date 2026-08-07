#!/bin/sh
set -eu
python3 /opt/socra/validate-adapters.py
set -- serve "${BASE_MODEL_NAME:-google/gemma-3-4b-it}" --host 0.0.0.0 --port 8001 --api-key "${MODEL_PRIMARY_API_KEY:?required}" --max-model-len "${VLLM_MAX_MODEL_LEN:-4096}" --gpu-memory-utilization "${VLLM_GPU_MEMORY_UTILIZATION:-0.80}" --max-num-seqs "${VLLM_MAX_NUM_SEQS:-1}"
[ -z "${VLLM_QUANTIZATION:-}" ] || set -- "$@" --quantization "$VLLM_QUANTIZATION"
[ -z "${VLLM_LOAD_FORMAT:-}" ] || set -- "$@" --load-format "$VLLM_LOAD_FORMAT"
if [ "${MODEL_PRIMARY_ADAPTER_ENABLED:-false}" = true ]; then set -- "$@" --enable-lora --lora-modules "socra-gemma-v1=${MODEL_PRIMARY_ADAPTER_PATH}"; [ "${MODEL_STABLE_ADAPTER_ENABLED:-false}" != true ] || set -- "$@" "socra-gemma-v0=${MODEL_STABLE_ADAPTER_PATH}"; else set -- "$@" --served-model-name "${MODEL_PRIMARY_NAME:-gemma-3-4b-base}"; fi
exec vllm "$@"
