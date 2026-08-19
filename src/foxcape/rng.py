"""Non-cryptographic randomness for human-like browser behavior.

Foxcape uses stdlib ``random`` for mouse paths, typing cadence, proxy rotation,
and warmup URL shuffling — never for secrets, tokens, or security-sensitive IDs.
All S2245 findings are consolidated here with explicit NOSONAR annotations.
"""

from __future__ import annotations

import random as _stdlib_random
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def sample(population: Sequence[T], k: int) -> list[T]:
    return _stdlib_random.sample(population, k)  # NOSONAR python:S2245


def choice(seq: Sequence[T]) -> T:
    return _stdlib_random.choice(seq)  # NOSONAR python:S2245


def choices(population: Sequence[T], weights: Sequence[float]) -> list[T]:
    return _stdlib_random.choices(population, weights=weights)  # NOSONAR python:S2245


def uniform(a: float, b: float) -> float:
    return _stdlib_random.uniform(a, b)  # NOSONAR python:S2245


def rand_float() -> float:
    return _stdlib_random.random()  # NOSONAR python:S2245


def gauss(mu: float, sigma: float) -> float:
    return _stdlib_random.gauss(mu, sigma)  # NOSONAR python:S2245


def randint(a: int, b: int) -> int:
    return _stdlib_random.randint(a, b)  # NOSONAR python:S2245


def lognormvariate(mu: float, sigma: float) -> float:
    return _stdlib_random.lognormvariate(mu, sigma)  # NOSONAR python:S2245


def paretovariate(alpha: float) -> float:
    return _stdlib_random.paretovariate(alpha)  # NOSONAR python:S2245
