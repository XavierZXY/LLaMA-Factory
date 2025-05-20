#!/bin/bash
export CUDA_VISIBLE_DEVICES=2,3,4,5
llamafactory-cli train examples/train_full/qwen2-3b-full-sft.yaml
# llamafactory-cli train examples/train_lora/qwen2-7b-lora-sft.yaml
