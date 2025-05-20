#!/bin/bash
CUDA_VISIBLE_DEVICES=1 API_PORT=10081 llamafactory-cli api \
    --model_name_or_path saves/qwen2-0.5b/full/sft/new_energy_issues_sharegpt_v2/checkpoint-2000 \
    --template qwen \
    --infer_backend vllm \
    --vllm_enforce_eager
    # --adapter_name_or_path saves/qwen3-8b/lora/sft-lora16/checkpoint-12400 \
    # --model_name_or_path Qwen/Qwen2.5-7B-Instruct \
# CUDA_VISIBLE_DEVICES=6,7 API_PORT=10080 llamafactory-cli api \
#     --model_name_or_path Qwen/Qwen3-8B \
#     --template qwen \
#     --infer_backend vllm \
#     --vllm_enforce_eager