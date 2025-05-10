#!/bin/bash
CUDA_VISIBLE_DEVICES=4,5 API_PORT=10082 llamafactory-cli api \
    --model_name_or_path saves/qwen3-1.7b/full/sft/empowerfactory/checkpoint-1440 \
    --template qwen \
    --infer_backend vllm \
    --vllm_enforce_eager
    # --model_name_or_path Qwen/Qwen2.5-7B-Instruct \
# CUDA_VISIBLE_DEVICES=6,7 API_PORT=10080 llamafactory-cli api \
#     --model_name_or_path Qwen/Qwen3-8B \
#     --template qwen \
#     --infer_backend vllm \
#     --vllm_enforce_eager