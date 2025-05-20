#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import argparse
from typing import List, Dict, Any, Optional

def convert_alpaca_to_openai(
    alpaca_data: List[Dict[str, Any]],
    system_prompt: str = "你是一个新能源相关问题的专家助手。",
) -> List[Dict[str, Any]]:
    """
    Convert Alpaca format data to OpenAI format.
    
    Args:
        alpaca_data: List of dictionaries in Alpaca format
        system_prompt: System prompt to add to each conversation
        
    Returns:
        List of dictionaries in OpenAI format
    """
    openai_data = []
    
    for item in alpaca_data:
        # Create the conversation
        messages = []
        
        # Add system prompt
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # Combine instruction and input for the user message
        user_message = item["instruction"]
        if item.get("input"):
            user_message = f"{user_message}\n\n{item['input']}"
        
        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Add assistant response
        messages.append({
            "role": "assistant",
            "content": item["output"]
        })
        
        # Create OpenAI format item
        openai_item = {
            "messages": messages
        }
        
        openai_data.append(openai_item)
    
    return openai_data

def main():
    parser = argparse.ArgumentParser(description="Convert Alpaca format to OpenAI format")
    parser.add_argument("input_file", help="Input file in Alpaca format")
    parser.add_argument("output_file", help="Output file in OpenAI format")
    parser.add_argument("--system-prompt", default="你是一个新能源相关问题的专家助手。",
                      help="System prompt to add to each conversation")
    
    args = parser.parse_args()
    
    # Read input file
    with open(args.input_file, "r", encoding="utf-8") as f:
        alpaca_data = json.load(f)
    
    # Convert data
    openai_data = convert_alpaca_to_openai(alpaca_data, args.system_prompt)
    
    # Write output file
    with open(args.output_file, "w", encoding="utf-8") as f:
        json.dump(openai_data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully converted {len(openai_data)} conversations from Alpaca to OpenAI format")

if __name__ == "__main__":
    main() 