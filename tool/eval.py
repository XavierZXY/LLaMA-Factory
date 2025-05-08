import asyncio
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

import openai
from dotenv import load_dotenv
from openai import AsyncOpenAI
from rich.console import Console
from rich.logging import RichHandler
from transformers import AutoTokenizer


load_dotenv()
# Set up rich logging
# Get current time for log filename
log_dir = f"log/{time.strftime('%Y%m%d')}"
os.makedirs(log_dir, exist_ok=True)  # Create directory if it doesn't exist
log_filename = f"{log_dir}/{time.strftime('%H%M%S')}.log"

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
client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "sk-123"),
    base_url=os.environ.get(
        "OPENAI_API_BASE",
        "http://127.0.0.1:10080/v1",
    ),
)
judge = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "sk-123"),
    base_url=os.environ.get(
        "OPENAI_API_BASE",
        "http://10.16.189.166:10080/v1",
    ),
)


def get_response(
    prompt="You are a helpful assistant.Give me a short answer",
):
    # Using OpenAI API instead of local model
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            # model="Qwen3-8B",  # or any other model like "gpt-4"
            model="test",  # or any other model like "gpt-4"
            messages=messages,
            max_tokens=512,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )

        return response.choices[0].message.content
    except Exception as e:
        log.error(f"Error calling OpenAI API: {e}")
        return "Error generating response"


def judge_qwen(answer, response):
    # Using OpenAI API instead of local Qwen model
    try:
        prompt = f"请检测以下两段文本的相似度是多少，特别要注意其中的参考文献，如果其中一个有参考文献，另一个没有参考文献，或者错误的参考文献，则不能高于6分。给出一个0-10的分数，其中0表示完全不相似，10表示完全相同。只需回复一个0-10之间的整数分数，不要有其他解释。参考答案: {answer}实际回答:{response}相似度分数(0-10):"

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
        # "./data_self/empowerfactory_test.json",
        "./data/relay_protection_issues_export.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    total_score = 0
    data_sample = data[:100]  # Sample first 100 items for evaluation
    max_possible_score = len(data_sample) * 10  # Maximum score is 10 per item

    log.info(f"Evaluating {len(data_sample)} items...")

    for i, item in enumerate(data_sample):
        instruction = item["instruction"]
        reference_output = item["output"]

        log.info(f"\nItem {i + 1}/{len(data_sample)}:")
        log.info(f"Instruction: {instruction}")
        log.info(
            f"Reference Output: {reference_output}"
        )  # Show beginning of reference output

        # 2. Get model response using the instruction
        model_response = get_response(instruction)
        log.info(
            f"Model response: {model_response}"
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


async def get_response_async(
    prompt="You are a helpful assistant.Give me a short answer",
):
    try:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {"role": "user", "content": prompt},
        ]

        response = await client.chat.completions.create(
            model="test",
            messages=messages,
            max_tokens=512,
            temperature=0.0,  # Set temperature to 0 for deterministic output
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )

        return response.choices[0].message.content
    except Exception as e:
        log.error(f"Error calling OpenAI API: {e}")
        return "Error generating response"


async def judge_qwen_async(answer, response):
    try:
        prompt = (
            "请检测以下两段文本的相似度是多少，特别要注意其中的参考文献，如果其中一个有参"
            "考文献，另一个没有参考文献，或者错误的参考文献，则不能高于6分。给出一个0-10的分数，"
            "其中0表示完全不相似，10表示完全相同。只需回复一个0-10之间的整数分数，不要有其他解释。"
            f"参考答案: {answer}实际回答:{response}相似度分数(0-10):"
        )

        messages = [
            {
                "role": "system",
                "content": "你是一个公正的评分助手，请根据指示给出准确的评分。",
            },
            {"role": "user", "content": prompt},
        ]

        completion = await judge.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=messages,
            max_tokens=10,
            temperature=0.0,
        )

        generated_text = completion.choices[0].message.content.strip()

        try:
            import re

            score_match = re.search(r"\b([0-9]|10)\b", generated_text)
            if score_match:
                score = int(score_match.group(1))
            else:
                score = 5
        except Exception:
            score = 5

        return score
    except Exception as e:
        log.error(f"Judge --- Error calling OpenAI API: {e}")
        return -1


async def process_item(item: Dict) -> int:
    instruction = item["instruction"]
    reference_output = item["output"]

    log.info(f"\nProcessing instruction: {instruction[:100]}...")

    model_response = await get_response_async(instruction)
    log.info(f"Model response: {model_response}")
    log.info(f"Reference output: {reference_output}")

    score = await judge_qwen_async(reference_output, model_response)

    log.info(f"Score: {score}/10")
    return score


async def main():
    # 1. Read data from JSON file
    with open(
        "./data/relay_protection_issues_export.json",
        "r",
        encoding="utf-8",
    ) as f:
        data = json.load(f)

    data_sample = data[:100]  # Sample first 100 items for evaluation
    max_possible_score = len(data_sample) * 10

    log.info(f"Evaluating {len(data_sample)} items...")

    # Process items concurrently with a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(16)  # Limit concurrent requests to 16

    async def process_with_semaphore(item):
        async with semaphore:
            return await process_item(item)

    tasks = [process_with_semaphore(item) for item in data_sample]
    scores = await asyncio.gather(*tasks)

    total_score = sum(scores)
    final_score_percentage = (total_score / max_possible_score) * 100

    log.info(f"\n=== Evaluation Complete ===")
    log.info(f"Total Score: {total_score}/{max_possible_score}")
    log.info(f"Normalized Score: {final_score_percentage:.2f}%")


if __name__ == "__main__":
    asyncio.run(main())
