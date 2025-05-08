#!/bin/bash
export CUDA_VISIBLE_DEVICES=0,1,2,3
llamafactory-cli train examples/train_lora/qwen3-8b-lora-sft.yaml
# llamafactory-cli train examples/train_lora/qwen2-7b-lora-sft.yaml
