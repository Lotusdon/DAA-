"""
Generate the 10 Closest Pair assignment datasets.

Usage:
    python generator/generate_closest_pair.py
    python generator/generate_closest_pair.py --small-only
    python generator/generate_closest_pair.py --output datasets/closest_pair --seed 20261110

Each dataset gets its own deterministic seed. Seeds are written to
seed_manifest.csv in the output folder.

The generator streams points to disk so million-point files do not need to
remain in memory.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
from pathlib import Path

DEFAULT_SEED = 20261110
FULL_COUNTS = {
    "cp01": 1_000,
    "cp02": 10_000,
    "cp03": 100_000,
    "cp04": 1_000_000,
    "cp05": 1_000_000,
    "cp06": 1_000_000,
    "cp07": 100_000,
    "cp08": 100_000,
    "cp09": 1_000_000,
    "cp10": 101,
}
SMALL_FILES = {"cp01", "cp02", "cp10"}


def uniform_points(rng: random.Random, n: int):
    for _ in range(n):
        yield rng.uniform(0, 1_000_000), rng.uniform(0, 1_000_000)


def clustered_points(rng: random.Random, n: int):
    centers = [(rng.uniform(50_000, 950_000),
                rng.uniform(50_000, 950_000)) for _ in range(10)]
    # Standard deviation 3,000 gives visible, compact clusters.
    for _ in range(n):
        cx, cy = centers[rng.randrange(10)]
        x = min(1_000_000, max(0, rng.gauss(cx, 3_000)))
        y = min(1_000_000, max(0, rng.gauss(cy, 3_000)))
        yield x, y


def duplicate_points(rng: random.Random, n: int):
    # A small coordinate range guarantees many repeated points and distance 0.
    for _ in range(n):
        yield rng.randint(0, 100), rng.randint(0, 100)


def vertical_line_points(rng: random.Random, n: int):
    for _ in range(n):
        yield 500_000, rng.randint(0, 1_000_000)


def grid_points(n: int):
    # A 317-column unit grid has enough positions for 100,000 points.
    columns = math.ceil(math.sqrt(n))
    for index in range(n):
        yield index % columns, index // columns


def middle_line_points(rng: random.Random, n: int):
    """
    Construct a guaranteed closest pair across x=500,000.

    The special points are (499999, 5) and (500001, 5), distance 2.
    Every other point is on a 10-unit lattice, so it is farther than 2 from
    either special point; distinct lattice points are at least 10 apart.
    """
    yield 499_999, 5
    yield 500_001, 5

    used = {(499_999, 5), (500_001, 5)}
    remaining = n - 2
    while remaining:
        # Pick a lattice point on either side of the dividing line.
        gx = rng.randrange(0, 100_001)
        x = gx * 10
        y = rng.randrange(0, 100_001) * 10
        point = (x, y)
        if point in used:
            continue
        used.add(point)
        yield point
        remaining -= 1


def small_demo_points():
    return [
        (2, 3), (12, 30), (40, 50), (5, 1), (12, 10),
        (3, 4), (8, 8), (20, 18), (25, 25), (30, 29),
        (11, 11), (50, 50), (51, 50), (70, 80), (90, 10),
        (15, 16), (18, 19), (22, 21), (35, 37), (45, 44),
        (60, 61), (65, 64), (75, 74), (85, 86), (95, 96),
        (100, 100), (110, 105), (120, 118), (130, 125), (140, 135),
        (150, 145), (160, 155), (170, 165), (180, 175), (190, 185),
        (200, 195), (210, 205), (220, 215), (230, 225), (240, 235),
        (250, 245), (260, 255), (270, 265), (280, 275), (290, 285),
        (300, 295), (310, 305), (320, 315), (330, 325), (340, 335),
        (350, 345), (360, 355), (370, 365), (380, 375), (390, 385),
        (400, 395), (410, 405), (420, 415), (430, 425), (440, 435),
        (450, 445), (460, 455), (470, 465), (480, 475), (490, 485),
        (500, 495), (510, 505), (520, 515), (530, 525), (540, 535),
        (550, 545), (560, 555), (570, 565), (580, 575), (590, 585),
        (600, 595), (610, 605), (620, 615), (630, 625), (640, 635),
        (650, 645), (660, 655), (670, 665), (680, 675), (690, 685),
        (700, 695), (710, 705), (720, 715), (730, 725), (740, 735),
        (750, 745), (760, 755), (770, 765), (780, 775), (790, 785),
        (800, 795), (810, 805), (820, 815), (830, 825), (840, 835),
        (850, 845), (860, 855), (870, 865), (880, 875), (890, 885),
        (900, 895), (910, 905), (920, 915), (930, 925), (940, 935),
        (950, 945), (960, 955), (970, 965), (980, 975), (990, 985),
        (1000, 995),
    ]


def generate_one(name: str, output_dir: Path, seed: int):
    n = FULL_COUNTS[name]
    rng = random.Random(seed)
    path = output_dir / f"{name}.txt"

    if name == "cp01" or name == "cp02" or name == "cp03" or name == "cp04":
        point_iter = uniform_points(rng, n)
    elif name == "cp05":
        point_iter = clustered_points(rng, n)
    elif name == "cp06":
        point_iter = duplicate_points(rng, n)
    elif name == "cp07":
        point_iter = vertical_line_points(rng, n)
    elif name == "cp08":
        point_iter = grid_points(n)
    elif name == "cp09":
        point_iter = middle_line_points(rng, n)
    elif name == "cp10":
        points = small_demo_points()
        if len(points) != n:
            raise RuntimeError(f"{name} must contain exactly {n} points.")
        point_iter = iter(points)
    else:
        raise ValueError(f"Unknown dataset: {name}")

    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(f"{n}\n")
        written = 0
        for x, y in point_iter:
            file.write(f"{x:.8f} {y:.8f}\n" if isinstance(x, float) or isinstance(y, float)
                       else f"{x} {y}\n")
            written += 1
        if written != n:
            raise RuntimeError(f"{name}: expected {n} points, wrote {written}.")

    return path


def main():
    parser = argparse.ArgumentParser(description="Generate closest-pair datasets.")
    parser.add_argument("--output", default="datasets/closest_pair",
                        help="Output directory (default: datasets/closest_pair)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"Base seed (default: {DEFAULT_SEED})")
    parser.add_argument("--small-only", action="store_true",
                        help="Generate only cp01, cp02 and cp10 (files under 1 MB).")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    names = sorted(SMALL_FILES if args.small_only else FULL_COUNTS.keys())
    manifest = []

    for index, name in enumerate(names):
        seed = args.seed + index
        path = generate_one(name, output_dir, seed)
        manifest.append((name, FULL_COUNTS[name], seed, path.stat().st_size))
        print(f"Created {path} | points={FULL_COUNTS[name]:,} | seed={seed} "
              f"| size={path.stat().st_size:,} bytes")

    manifest_path = output_dir / "seed_manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["filename", "number_of_points", "seed", "file_size_bytes"])
        writer.writerows(manifest)
    print(f"\nSeed manifest saved to: {manifest_path}")


if __name__ == "__main__":
    main()

