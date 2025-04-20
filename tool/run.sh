#!/bin/bash
CUDA_VISIBLE_DEVICES=0,1 API_PORT=10080 llamafactory-cli api \
    --model_name_or_path Qwen/Qwen2.5-7B-Instruct \
    --adapter_name_or_path saves/qwen2-7b/lora/sft-4Batches \
    --template qwen \
    --infer_backend vllm \
    --vllm_enforce_eager
    # --model_name_or_path Qwen/Qwen2.5-7B-Instruct \