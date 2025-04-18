#!/bin/bash
CUDA_VISIBLE_DEVICES=2,3 API_PORT=10081 llamafactory-cli api \
    --model_name_or_path Qwen/Qwen2.5-7B-Instruct \
    --template qwen \
    --infer_backend vllm \
    --vllm_enforce_eager