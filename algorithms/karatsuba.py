"""
Karatsuba multiplication using decimal strings.

This avoids Python's maximum decimal-string-to-int conversion limit and supports
very large inputs. Schoolbook multiplication is used below BASE_CASE_DIGITS.

Public function:
    karatsuba_multiply(a, b, collect_steps=False)

Returns:
    (product_as_string, steps)
"""
from __future__ import annotations

BASE_CASE_DIGITS = 32


def _normalize(number: str) -> str:
    number = str(number).strip()
    if not number or not number.isdigit():
        raise ValueError("Inputs must be non-negative integers containing digits only.")
    return number.lstrip("0") or "0"


def _add(a: str, b: str) -> str:
    i, j, carry = len(a) - 1, len(b) - 1, 0
    out = []
    while i >= 0 or j >= 0 or carry:
        total = carry
        if i >= 0:
            total += ord(a[i]) - 48
            i -= 1
        if j >= 0:
            total += ord(b[j]) - 48
            j -= 1
        out.append(chr(48 + total % 10))
        carry = total // 10
    return "".join(reversed(out)).lstrip("0") or "0"


def _subtract(a: str, b: str) -> str:
    """Return a-b; requires a >= b."""
    if len(a) < len(b) or (len(a) == len(b) and a < b):
        raise ValueError("Internal subtraction would be negative.")
    i, j, borrow = len(a) - 1, len(b) - 1, 0
    out = []
    while i >= 0:
        digit = ord(a[i]) - 48 - borrow
        if j >= 0:
            digit -= ord(b[j]) - 48
            j -= 1
        borrow = 1 if digit < 0 else 0
        if borrow:
            digit += 10
        out.append(chr(48 + digit))
        i -= 1
    return "".join(reversed(out)).lstrip("0") or "0"


def _schoolbook(a: str, b: str) -> str:
    if a == "0" or b == "0":
        return "0"
    result = [0] * (len(a) + len(b))
    aa = [ord(c) - 48 for c in a]
    bb = [ord(c) - 48 for c in b]
    for i in range(len(aa) - 1, -1, -1):
        for j in range(len(bb) - 1, -1, -1):
            result[i + j + 1] += aa[i] * bb[j]
    for k in range(len(result) - 1, 0, -1):
        carry, result[k] = divmod(result[k], 10)
        result[k - 1] += carry
    return "".join(map(str, result)).lstrip("0") or "0"


def _shift(number: str, places: int) -> str:
    if number == "0":
        return "0"
    return number + ("0" * places)


def karatsuba_multiply(a: str, b: str, collect_steps: bool = False):
    a, b = _normalize(a), _normalize(b)
    steps = []

    def multiply(x: str, y: str, depth: int = 0) -> str:
        x, y = _normalize(x), _normalize(y)
        if x == "0" or y == "0":
            if collect_steps:
                steps.append({"type": "zero", "depth": depth,
                              "digits_a": len(x), "digits_b": len(y)})
            return "0"

        if min(len(x), len(y)) <= BASE_CASE_DIGITS:
            product = _schoolbook(x, y)
            if collect_steps:
                steps.append({"type": "schoolbook", "depth": depth,
                              "a": x, "b": y, "product": product})
            return product

        # Split relative to the longer operand; empty high part becomes zero.
        n = max(len(x), len(y))
        half = n // 2
        x_high, x_low = (x[:-half] or "0"), x[-half:]
        y_high, y_low = (y[:-half] or "0"), y[-half:]

        if collect_steps:
            steps.append({
                "type": "split", "depth": depth,
                "a": x, "b": y,
                "a_high": x_high, "a_low": x_low,
                "b_high": y_high, "b_low": y_low,
            })

        z0 = multiply(x_low, y_low, depth + 1)
        z2 = multiply(x_high, y_high, depth + 1)
        z1 = multiply(_add(x_low, x_high), _add(y_low, y_high), depth + 1)
        middle = _subtract(_subtract(z1, z2), z0)

        result = _add(
            _add(_shift(z2, 2 * half), _shift(middle, half)),
            z0
        )
        if collect_steps:
            steps.append({
                "type": "combine", "depth": depth,
                "z0": z0, "z1": z1, "z2": z2,
                "middle": middle, "product": result,
            })
        return result

    return multiply(a, b), steps


def read_multiplication_file(path: str):
    """Read the assignment format: two lines, one non-negative integer each."""
    with open(path, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]
    if len(lines) != 2:
        raise ValueError("Multiplication file must contain exactly two non-empty lines.")
    return _normalize(lines[0]), _normalize(lines[1])

