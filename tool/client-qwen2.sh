#!/bin/bash
CUDA_VISIBLE_DEVICES=4,5 API_PORT=10082 llamafactory-cli api \
    --model_name_or_path Qwen/Qwen3-8B \
    --adapter_name_or_path saves/qwen3-8b/lora/sft-lora16-rank32/relay_protection_issues_export/checkpoint-200 \
    --template qwen \
    --infer_backend vllm \
    --vllm_enforce_eager
    # --model_name_or_path Qwen/Qwen2.5-7B-Instruct \
# CUDA_VISIBLE_DEVICES=6,7 API_PORT=10080 llamafactory-cli api \
#     --model_name_or_path Qwen/Qwen3-8B \
#     --template qwen \
#     --infer_backend vllm \
#     --vllm_enforce_eager