"""
Generate the 10 Karatsuba assignment datasets.

Usage:
    python generator/generate_multiplication.py
    python generator/generate_multiplication.py --small-only
    python generator/generate_multiplication.py --output datasets/multiplication --seed 20261110

Each dataset gets its own deterministic seed. Seeds are written to
seed_manifest.csv. Large digit strings are generated in chunks.
"""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

DEFAULT_SEED = 20261110
SMALL_FILES = {"im01", "im02", "im03", "im06", "im07", "im10"}


def random_digits(rng: random.Random, length: int) -> str:
    if length < 1:
        raise ValueError("Digit length must be at least 1.")
    first = str(rng.randint(1, 9))
    chunks = []
    remaining = length - 1
    chunk_size = 50_000
    while remaining:
        take = min(chunk_size, remaining)
        chunks.append("".join(str(rng.randrange(10)) for _ in range(take)))
        remaining -= take
    return first + "".join(chunks)


def random_digits_with_zeros(rng: random.Random, length: int) -> str:
    """Odd-length number containing many zeros (roughly 70% zero digits)."""
    first = str(rng.randint(1, 9))
    tail = []
    for _ in range(length - 1):
        tail.append("0" if rng.random() < 0.70 else str(rng.randrange(1, 10)))
    return first + "".join(tail)


def power_of_ten(digits: int) -> str:
    # A 1 followed by digits-1 zeros is 10 ** (digits-1).
    return "1" + ("0" * (digits - 1))


def write_dataset(path: Path, number_a: str, number_b: str):
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(number_a)
        file.write("\n")
        file.write(number_b)
        file.write("\n")


def generate_one(name: str, output_dir: Path, seed: int):
    rng = random.Random(seed)

    if name == "im01":
        a, b = random_digits(rng, 1_000), random_digits(rng, 1_000)
    elif name == "im02":
        a, b = random_digits(rng, 10_000), random_digits(rng, 10_000)
    elif name == "im03":
        a, b = random_digits(rng, 100_000), random_digits(rng, 100_000)
    elif name == "im04":
        a, b = random_digits(rng, 1_000_000), random_digits(rng, 1_000_000)
    elif name == "im05":
        a, b = random_digits(rng, 1_000_000), random_digits(rng, 10)
    elif name == "im06":
        a, b = "9" * 100_000, random_digits(rng, 100_000)
    elif name == "im07":
        a = random_digits_with_zeros(rng, 99_999)
        b = random_digits_with_zeros(rng, 99_999)
    elif name == "im08":
        a, b = power_of_ten(1_000_000), power_of_ten(1_000_000)
    elif name == "im09":
        a, b = "0", random_digits(rng, 1_000_000)
    elif name == "im10":
        a, b = random_digits(rng, 101), random_digits(rng, 101)
    else:
        raise ValueError(f"Unknown dataset: {name}")

    path = output_dir / f"{name}.txt"
    write_dataset(path, a, b)
    return path, len(a), len(b)


def main():
    parser = argparse.ArgumentParser(description="Generate Karatsuba multiplication datasets.")
    parser.add_argument("--output", default="datasets/multiplication",
                        help="Output directory (default: datasets/multiplication)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"Base seed (default: {DEFAULT_SEED})")
    parser.add_argument("--small-only", action="store_true",
                        help="Generate only files expected to be smaller than 1 MB.")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    all_names = [f"im{i:02d}" for i in range(1, 11)]
    names = sorted(SMALL_FILES if args.small_only else all_names)
    manifest = []

    for index, name in enumerate(names):
        seed = args.seed + index
        path, digits_a, digits_b = generate_one(name, output_dir, seed)
        manifest.append((name, digits_a, digits_b, seed, path.stat().st_size))
        print(f"Created {path} | digits=({digits_a:,}, {digits_b:,}) "
              f"| seed={seed} | size={path.stat().st_size:,} bytes")

    manifest_path = output_dir / "seed_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "digits_number_a", "digits_number_b",
                         "seed", "file_size_bytes"])
        writer.writerows(manifest)
    print(f"\nSeed manifest saved to: {manifest_path}")


if __name__ == "__main__":
    main()

