import json
import logging
import os
from typing import Dict, List

# OpenAI API configuration
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.logging import RichHandler
from tqdm import tqdm


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
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "sk-123"),
    base_url=os.environ.get("OPENAI_API_BASE", "http://127.0.0.1:10080/v1"),
)


def load_json_data(file_path: str) -> list[dict]:
    """Load JSON data from file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json_data(data: list[dict], file_path: str):
    """Save JSON data to file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def rewrite_with_gpt(instruction: str, output: str) -> list[tuple]:
    """Rewrite instruction and output using GPT to generate 5 different versions."""
    prompt = f"""请帮我将以下问题和答案改写成5个不同的版本，每个版本都要保持原意但使用完全不同的表达方式。要求：
1. 每个问题(instruction)都需要完全改写，使用不同的表达方式但保持原意
2. 每个答案(output)可以简单改写，但不要改变原意或产生歧义
3. 保持中文输出
4. 5个版本之间要有明显的区别，不能过于相似

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
        response = client.chat.completions.create(
            model="Qwen/Qwen3-30B-A3B",  # 可以根据需要更换模型
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的文本改写助手，擅长用不同的表达方式重写文本，同时保持原意。你需要为每个输入生成5个完全不同的改写版本。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,  # 增加温度以获得更多样化的输出
        )

        result = json.loads(response.choices[0].message.content)
        return [
            (version["instruction"], version["output"])
            for version in result["versions"]
        ]
    except Exception as e:
        logger.error(f"Error in rewriting: {e}")
        return [] * 5  # 如果出错，返回5个原始版本


def main():
    # 输入和输出文件路径
    input_file = "./data/relay_protection_issues_export_mini.json"
    output_file = "./data/rewritten_output.json"

    # 加载数据
    data = load_json_data(input_file)

    # 检查是否存在已处理的文件，如果存在则加载
    rewritten_data = []
    if os.path.exists(output_file):
        rewritten_data = load_json_data(output_file)
        logger.info(
            f"Found existing output file with {len(rewritten_data)} items"
        )

    # 计算已处理的原始数据数量
    processed_count = len(rewritten_data) // 5 if rewritten_data else 0

    # 改写数据
    for item in tqdm(
        data[processed_count:],
        desc="Rewriting instructions",
        initial=processed_count,
    ):
        try:
            # 获取5个改写版本
            versions = rewrite_with_gpt(item["instruction"], item["output"])

            if not versions:  # 如果生成失败，跳过当前项
                logger.warning(
                    f"Skipping item due to generation failure: {item['instruction'][:50]}..."
                )
                continue

            # 为每个版本创建新的数据项并立即写入文件
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
            # 保存当前进度
            save_json_data(rewritten_data, output_file)
            continue

    logger.info(f"Rewriting completed. Results saved to {output_file}")
    logger.info(
        f"Original items: {len(data)}, Rewritten items: {len(rewritten_data)}"
    )


if __name__ == "__main__":
    main()
