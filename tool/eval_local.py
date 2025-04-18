from transformers import AutoModelForCausalLM, AutoTokenizer


def get_response(
    prompt="Give me a short introduction to large language model.",
):
    device = "cuda"  # the device to load the model onto
    model_name_or_path = (
        "/home/zxy/codes/working/LLaMA-Factory/models/qwen2-7b-sft-lora-merged"
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path, torch_dtype="auto", device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)

    generated_ids = model.generate(model_inputs.input_ids, max_new_tokens=512)
    generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
        0
    ]
    return response


def judge_qwen(answer, response):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    # Set the specific CUDA devices to use (3 and 4)
    device_map = {"": [3, 4]}

    # Load Qwen2.5-7B model
    model_path = "Qwen/Qwen2.5-7B"
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.float16,
        device_map=device_map,
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_path, trust_remote_code=True
    )

    # Create evaluation prompt
    prompt = f"请检测以下两段文本的相似度是多少，特别是其中的参考文献。给出一个0-10的分数，其中0表示完全不相似，10表示完全相同。只需回复一个0-10之间的整数分数，不要有其他解释。参考答案: {answer}实际回答:{response}相似度分数(0-10):"

    # Prepare input for model
    messages = [
        {
            "role": "system",
            "content": "你是一个公正的评分助手，请根据指示给出准确的评分。",
        },
        {"role": "user", "content": prompt},
    ]

    text = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    # Generate response
    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=10,  # Short output since we just need a score
        temperature=0.0,  # Deterministic output
    )

    # Extract generated text
    generated_text = tokenizer.batch_decode(
        [generated_ids[0][len(model_inputs.input_ids[0]) :]],
        skip_special_tokens=True,
    )[0].strip()

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


def main():
    import json
    import time

    # 1. Read data from JSON file
    with open(
        "./data/ChemistrySpecialtyIssues.json", "r", encoding="utf-8"
    ) as f:
        data = json.load(f)

    total_score = 0
    max_possible_score = len(data) * 10  # Maximum score is 10 per item

    print(f"Evaluating {len(data)} items...")

    for i, item in enumerate(data):
        instruction = item["instruction"]
        reference_output = item["output"]

        print(f"\nItem {i + 1}/{len(data)}:")
        print(f"Instruction: {instruction}")

        # 2. Get model response using the instruction
        model_response = get_response(instruction)
        print(
            f"Model response: {model_response[:100]}..."
        )  # Show beginning of response

        # 3. Judge the quality of the response
        score = judge_qwen(reference_output, model_response)
        print(f"Score: {score}/10")

        # 4. Accumulate scores
        total_score += score
        time.sleep(1)  # Add slight delay between evaluations

    # 5. Normalize score to percentage
    final_score_percentage = (total_score / max_possible_score) * 100

    print(f"\n=== Evaluation Complete ===")
    print(f"Total Score: {total_score}/{max_possible_score}")
    print(f"Normalized Score: {final_score_percentage:.2f}%")


if __name__ == "__main__":
    main()
