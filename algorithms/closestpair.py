"""
Closest pair of points using O(n log n) divide and conquer.

Public function:
    closest_pair(points, collect_steps=False)
where points is an iterable of (x, y) pairs.

Returns:
    (point_a, point_b, distance, steps)

The steps list contains compact recursion summaries suitable for a small-input
step viewer. For large inputs, leave collect_steps=False.
"""
from __future__ import annotations

import math
from typing import Iterable


def closest_pair(points: Iterable[tuple[float, float]], collect_steps: bool = False):
    pts = [(float(x), float(y), i) for i, (x, y) in enumerate(points)]
    n = len(pts)
    if n < 2:
        raise ValueError("Closest pair requires at least two points.")

    steps = []

    # Sort once by x and once by y. The original index distinguishes duplicates.
    px = sorted(pts, key=lambda p: (p[0], p[1], p[2]))
    py = sorted(pts, key=lambda p: (p[1], p[0], p[2]))

    def distance_sq(a, b):
        return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

    def better(best, candidate):
        if best is None or candidate[0] < best[0]:
            return candidate
        return best

    def brute_force(arr):
        best = None
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                cand = (distance_sq(arr[i], arr[j]), arr[i], arr[j])
                best = better(best, cand)
        return best

    def solve(x_sorted, y_sorted, depth=0):
        size = len(x_sorted)
        if size <= 3:
            best = brute_force(x_sorted)
            if collect_steps:
                steps.append({
                    "type": "base_case",
                    "depth": depth,
                    "size": size,
                    "points": [(p[0], p[1]) for p in x_sorted],
                    "best_distance": math.sqrt(best[0]),
                })
            return best

        mid = size // 2
        left_x = x_sorted[:mid]
        right_x = x_sorted[mid:]
        left_ids = {p[2] for p in left_x}
        left_y, right_y = [], []
        for p in y_sorted:
            (left_y if p[2] in left_ids else right_y).append(p)

        split_x = right_x[0][0]
        if collect_steps:
            steps.append({
                "type": "divide",
                "depth": depth,
                "size": size,
                "split_x": split_x,
                "left_size": len(left_x),
                "right_size": len(right_x),
            })

        best_left = solve(left_x, left_y, depth + 1)
        best_right = solve(right_x, right_y, depth + 1)
        best = better(best_left, best_right)
        delta = math.sqrt(best[0])

        # The strip is already sorted by y because it is filtered from y_sorted.
        strip = [p for p in y_sorted if abs(p[0] - split_x) < delta]
        strip_checks = 0
        for i in range(len(strip)):
            # At most the next 7 points need to be checked in 2D.
            for j in range(i + 1, min(i + 8, len(strip))):
                if (strip[j][1] - strip[i][1]) >= math.sqrt(best[0]):
                    break
                strip_checks += 1
                best = better(best, (distance_sq(strip[i], strip[j]), strip[i], strip[j]))

        if collect_steps:
            steps.append({
                "type": "combine",
                "depth": depth,
                "size": size,
                "strip_size": len(strip),
                "strip_checks": strip_checks,
                "best_distance": math.sqrt(best[0]),
            })
        return best

    best_sq, a, b = solve(px, py)
    return (a[0], a[1]), (b[0], b[1]), math.sqrt(best_sq), steps


def read_points_file(path: str):
    """Read the assignment format: n on line 1, then n lines of 'x y'."""
    with open(path, "r", encoding="utf-8") as file:
        first = file.readline().strip()
        if not first:
            raise ValueError("The points file is empty.")
        n = int(first)
        points = []
        for line_number in range(2, n + 2):
            line = file.readline()
            if not line:
                raise ValueError(f"Expected {n} points, but the file ended early.")
            parts = line.split()
            if len(parts) != 2:
                raise ValueError(f"Invalid point on line {line_number}: {line!r}")
            points.append((float(parts[0]), float(parts[1])))
    return points

