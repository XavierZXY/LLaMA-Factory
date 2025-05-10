import json
import logging
import os
import asyncio
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor

# OpenAI API configuration
from dotenv import load_dotenv
from openai import AsyncOpenAI
from rich.console import Console
from rich.logging import RichHandler
from tqdm.asyncio import tqdm_asyncio


# Setup rich console and logging
console = Console()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("rich")


load_dotenv()
client = AsyncOpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "sk-123"),
    base_url=os.environ.get("OPENAI_API_BASE", "http://127.0.0.1:10080/v1"),
)

# 并发控制参数
MAX_CONCURRENT_REQUESTS = 5  # 同时处理的最大请求数
BATCH_SIZE = 24  # 每批处理的数据量


def load_json_data(file_path: str) -> list[dict]:
    """Load JSON data from file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_data(data: list[dict], file_path: str):
    """Save JSON data to file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


async def rewrite_with_gpt(instruction: str, output: str) -> list[tuple]:
    """Rewrite instruction and output using GPT to generate 5 different versions."""
    prompt = f"""请帮我将以下问题和答案改写成5个不同的版本，每个版本都要保持原意但使用完全不同的表达方式。要求：
1. 每个问题(instruction)都需要完全改写，使用不同的表达方式但保持原意，如有参考文献，不要省略参考文献
2. 每个答案(output)可以简单改写，但不要改变原意或产生歧义，不要过度减少文本长度，如有参考文献，不要省略参考文献
3. 保持中文输出
4. 5个版本之间的instruction要有明显的区别，不能过于相似
5. 只返回JSON格式的结果，不要添加任何其他内容

原始问题：{instruction}
原始答案：{output}

请按照以下JSON格式返回：
{{
    "versions": [
        {{
            "instruction": "改写后的问题1",
            "output": "改写后的答案1"
        }},
        {{
            "instruction": "改写后的问题2",
            "output": "改写后的答案2"
        }},
        {{
            "instruction": "改写后的问题3",
            "output": "改写后的答案3"
        }},
        {{
            "instruction": "改写后的问题4",
            "output": "改写后的答案4"
        }},
        {{
            "instruction": "改写后的问题5",
            "output": "改写后的答案5"
        }}
    ]
}}"""

    try:
        response = await client.chat.completions.create(
            model="Qwen/Qwen3-30B-A3B",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的文本改写助手，擅长用不同的表达方式重写文本，同时保持原意。你需要为每个输入生成5个完全不同的改写版本。不要使用思考模式，严格按照指定格式返回结果。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
        )

        result = json.loads(response.choices[0].message.content)
        return [
            (version["instruction"], version["output"])
            for version in result["versions"]
        ]
    except Exception as e:
        logger.error(f"Error in rewriting: {e}")
        return [] * 5


async def process_batch(batch: List[dict], rewritten_data: List[dict], output_file: str) -> None:
    """Process a batch of items concurrently."""
    tasks = []
    for item in batch:
        task = asyncio.create_task(rewrite_with_gpt(item["instruction"], item["output"]))
        tasks.append((item, task))
    
    for item, task in tasks:
        try:
            versions = await task
            if not versions:
                logger.warning(f"Skipping item due to generation failure: {item['instruction'][:50]}...")
                continue

            for new_instruction, new_output in versions:
                rewritten_item = {
                    "instruction": new_instruction,
                    "input": item["input"],
                    "output": new_output,
                }
                rewritten_data.append(rewritten_item)
                
                # 每生成一个版本就保存一次
                save_json_data(rewritten_data, output_file)
                
        except Exception as e:
            logger.error(f"Error processing item: {e}")
            save_json_data(rewritten_data, output_file)


async def main():
    # 输入和输出文件路径
    input_file = "./data/relay_protection_issues_export.json"
    output_file = "./data/rewritten/relay_protection_issues_export.json"

    # 加载数据
    data = load_json_data(input_file)

    # 检查是否存在已处理的文件，如果存在则加载
    rewritten_data = []
    if os.path.exists(output_file):
        rewritten_data = load_json_data(output_file)
        logger.info(f"Found existing output file with {len(rewritten_data)} items")

    # 计算已处理的原始数据数量
    processed_count = len(rewritten_data) // 5 if rewritten_data else 0
    remaining_data = data[processed_count:]

    # 将数据分成批次处理
    for i in range(0, len(remaining_data), BATCH_SIZE):
        batch = remaining_data[i:i + BATCH_SIZE]
        await process_batch(batch, rewritten_data, output_file)
        logger.info(f"Processed batch {i//BATCH_SIZE + 1}/{(len(remaining_data) + BATCH_SIZE - 1)//BATCH_SIZE}")

    logger.info(f"Rewriting completed. Results saved to {output_file}")
    logger.info(f"Original items: {len(data)}, Rewritten items: {len(rewritten_data)}")


if __name__ == "__main__":
    asyncio.run(main())
