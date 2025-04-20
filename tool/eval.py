import json
import logging
import os
import time

import openai
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.logging import RichHandler
from transformers import AutoTokenizer


load_dotenv()
# Set up rich logging
# Get current time for log filename
# log_filename = f"eval_{time.strftime('%Y%m%d_%H%M%S')}.log"
log_filename = "log/4Batch.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, markup=True),
        logging.FileHandler(log_filename, mode="w", encoding="utf-8"),
    ],
)

log = logging.getLogger("eval")

# Initialize OpenAI client
client = OpenAI(
    api_key=os.environ.get(
        "OPENAI_API_KEY", "sk-123"
    ),  # Get API key from environment variable or replace with your key
    base_url=os.environ.get(
        "OPENAI_API_BASE", "http://127.0.0.1:10080/v1"
    ),  # Optional: configure custom base URL
)
judge = OpenAI(
    api_key=os.environ.get(
        "OPENAI_API_KEY", "sk-123"
    ),  # Get API key from environment variable or replace with your key
    base_url=os.environ.get(
        # "OPENAI_API_BASE", "https://api.siliconflow.cn/v1"
        "OPENAI_API_BASE",
        "http://127.0.0.1:10081/v1",
    ),  # Optional: configure custom base URL
)


def get_response(
    prompt="Give me a short introduction to large language model.",
):
    # Using OpenAI API instead of local model
    try:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            model="test",  # or any other model like "gpt-4"
            messages=messages,
            max_tokens=512,
        )

        return response.choices[0].message.content
    except Exception as e:
        log.error(f"Error calling OpenAI API: {e}")
        return "Error generating response"


def judge_qwen(answer, response):
    # Using OpenAI API instead of local Qwen model
    try:
        prompt = f"请检测以下两段文本的相似度是多少，特别要注意其中的参考文献，如果其中一个有参考文献，另一个没有参考文献，或者错误的参考文献，则不能高于5分。给出一个0-10的分数，其中0表示完全不相似，10表示完全相同。只需回复一个0-10之间的整数分数，不要有其他解释。参考答案: {answer}实际回答:{response}相似度分数(0-10):"

        messages = [
            {
                "role": "system",
                "content": "你是一个公正的评分助手，请根据指示给出准确的评分。",
            },
            {"role": "user", "content": prompt},
        ]

        completion = judge.chat.completions.create(
            # model="THUDM/GLM-4-32B-0414",  # Using GPT-4 for better evaluation
            model="Qwen/Qwen2.5-7B-Instruct",  # Using GPT-4 for better evaluation
            messages=messages,
            max_tokens=10,
            temperature=0.0,  # Deterministic output
        )

        generated_text = completion.choices[0].message.content.strip()

        # Extract the score from the generated text
        try:
            # Try to extract numeric score from response
            import re

            score_match = re.search(r"\b([0-9]|10)\b", generated_text)
            if score_match:
                score = int(score_match.group(1))
            else:
                # Default score if no match found
                score = 5
        except Exception:
            score = 5

        return score
    except Exception as e:
        log.error(f"Judge --- Error calling OpenAI API: {e}")
        return -1


def main():
    # 1. Read data from JSON file
    with open(
        "./data_self/test/ChemistrySpecialtyIssues_test.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    total_score = 0
    max_possible_score = len(data) * 10  # Maximum score is 10 per item

    log.info(f"Evaluating {len(data)} items...")

    for i, item in enumerate(data[:200]):
        instruction = item["instruction"]
        reference_output = item["output"]

        log.info(f"\nItem {i + 1}/{len(data)}:")
        log.info(f"Instruction: {instruction}")
        log.info(
            f"Reference Output: {reference_output[:100]}..."
        )  # Show beginning of reference output

        # 2. Get model response using the instruction
        model_response = get_response(instruction)
        log.info(
            f"Model response: {model_response[:100]}..."
        )  # Show beginning of response

        # 3. Judge the quality of the response
        score = judge_qwen(reference_output, model_response)
        log.info(f"Score: {score}/10")

        # 4. Accumulate scores
        total_score += score
        time.sleep(1)  # Add slight delay between evaluations

    # 5. Normalize score to percentage
    final_score_percentage = (total_score / max_possible_score) * 100

    log.info(f"\n=== Evaluation Complete ===")
    log.info(f"Total Score: {total_score}/{max_possible_score}")
    log.info(f"Normalized Score: {final_score_percentage:.2f}%")


if __name__ == "__main__":
    main()
