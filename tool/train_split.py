import argparse
import json
import os
import random
from pathlib import Path


def split_dataset(input_file, output_dir, test_ratio=0.2, seed=42):
    """Split a dataset into training and testing sets.

    Args:
        input_file: Path to the input JSON file
        output_dir: Directory to save the output files
        test_ratio: Ratio of data to use for testing (default: 0.2)
        seed: Random seed for reproducibility
    """
    # Set random seed for reproducibility
    random.seed(seed)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load the dataset
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Shuffle the data
    random.shuffle(data)

    # Calculate split index
    split_idx = int(len(data) * test_ratio)

    # Split the data
    test_data = data[:split_idx]
    train_data = data[split_idx:]

    # Get base filename without extension
    base_name = Path(input_file).stem

    # Save test data
    test_file = os.path.join(output_dir, f"{base_name}_test.json")
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    # Save train data
    train_file = os.path.join(output_dir, f"{base_name}_train.json")
    with open(train_file, "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)

    print(f"Total data: {len(data)} items")
    print(
        f"Train data: {len(train_data)} items ({len(train_data) / len(data):.1%})"
    )
    print(
        f"Test data: {len(test_data)} items ({len(test_data) / len(data):.1%})"
    )
    print(f"Files saved to {output_dir}")


def split_dataset_by_interval(input_file, output_dir, interval=5):
    """Split a dataset by taking every nth sample as test data.

    Args:
        input_file: Path to the input JSON file
        output_dir: Directory to save the output files
        interval: Take every nth sample as test data (default: 5)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load the dataset
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Split the data by taking every nth sample
    test_data = data[::interval]
    train_data = [item for i, item in enumerate(data) if i % interval != 0]

    # Get base filename without extension
    base_name = Path(input_file).stem

    # Save test data
    test_file = os.path.join(output_dir, f"{base_name}_test.json")
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    # Save train data
    train_file = os.path.join(output_dir, f"{base_name}_train.json")
    with open(train_file, "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)

    print(f"Total data: {len(data)} items")
    print(
        f"Train data: {len(train_data)} items ({len(train_data) / len(data):.1%})"
    )
    print(
        f"Test data: {len(test_data)} items ({len(test_data) / len(data):.1%})"
    )
    print(f"Files saved to {output_dir}")


def extract_first_n_samples(input_file, output_dir, n_samples=200):
    """Extract first N samples from the dataset as test set.

    Args:
        input_file: Path to the input JSON file
        output_dir: Directory to save the output files
        n_samples: Number of samples to extract as test set (default: 200)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load the dataset
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Split the data by taking first N samples
    test_data = data[:n_samples]
    train_data = data[n_samples:]

    # Get base filename without extension
    base_name = Path(input_file).stem

    # Save test data
    test_file = os.path.join(output_dir, f"{base_name}_test.json")
    with open(test_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    # Save train data
    train_file = os.path.join(output_dir, f"{base_name}_train.json")
    with open(train_file, "w", encoding="utf-8") as f:
        json.dump(train_data, f, ensure_ascii=False, indent=2)

    print(f"Total data: {len(data)} items")
    print(
        f"Train data: {len(train_data)} items ({len(train_data) / len(data):.1%})"
    )
    print(
        f"Test data: {len(test_data)} items ({len(test_data) / len(data):.1%})"
    )
    print(f"Files saved to {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split dataset into training and testing sets"
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="./train",
        help="Directory to save the output files",
    )
    parser.add_argument(
        "--test-ratio",
        "-r",
        type=float,
        default=0.1,
        help="Ratio of data to use for testing",
    )
    parser.add_argument(
        "--seed",
        "-s",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--split-method",
        "-m",
        choices=["random", "interval", "first_n"],
        default="random",
        help="Method to split the dataset: 'random' for random split, 'interval' for taking every nth sample, 'first_n' for taking first N samples",
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=5,
        help="Interval for splitting data (used when split-method is 'interval')",
    )
    parser.add_argument(
        "--n-samples",
        "-n",
        type=int,
        default=200,
        help="Number of samples to extract as test set (used when split-method is 'first_n')",
    )

    args = parser.parse_args()

    data_list = output_list = [
        "data_self/firepower/firepower.json",
    ]
    for input in data_list:
        if args.split_method == "random":
            split_dataset(input, args.output_dir, args.test_ratio, args.seed)
        elif args.split_method == "interval":
            split_dataset_by_interval(input, args.output_dir, args.interval)
        else:  # first_n
            extract_first_n_samples(input, args.output_dir, args.n_samples)
