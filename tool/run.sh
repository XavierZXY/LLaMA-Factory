#!/bin/bash
CUDA_VISIBLE_DEVICES=0,1 API_PORT=10080 llamafactory-cli api \
    --model_name_or_path /home/zxy/codes/working/LLaMA-Factory/models/qwen2-7b-sft-lora-merged \
    --template qwen \
    --infer_backend vllm \
    --vllm_enforce_eager