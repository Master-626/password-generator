"""
Core password generation and strength checking logic.
"""

import math
import secrets
import string
from typing import Dict, List


def generate_password(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """Generate a password using the operating system's secure random source.

    Every enabled category is represented, so length must be at least the
    number of enabled categories. Ambiguous characters are excluded from every
    choice when requested.
    """
    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError("Password length must be an integer")

    pools = []

    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append("!@#$%^&*()_+-=[]{}|;:,.<>?")

    if exclude_ambiguous:
        ambiguous = "Il1O0"
        pools = ["".join(c for c in pool if c not in ambiguous) for pool in pools]

    if not pools:
        raise ValueError("At least one character type must be enabled")

    if length < len(pools):
        raise ValueError(
            "Password length must be at least the number of enabled character types "
            f"({len(pools)})"
        )

    chars = "".join(pools)
    # Rejection sampling keeps all passwords satisfying the category rules
    # equally likely, without a predictable PRNG or a biased seed-and-shuffle.
    while True:
        password = "".join(secrets.choice(chars) for _ in range(length))
        if all(any(c in pool for c in password) for pool in pools):
            return password


def batch_generate(
    count: int = 10,
    length: int = 16,
    **kwargs,
) -> List[str]:
    """Generate multiple passwords; count must be a non-negative integer."""
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("Password count must be an integer")
    if count < 0:
        raise ValueError("Password count must be non-negative")
    return [generate_password(length=length, **kwargs) for _ in range(count)]


def evaluate_password_strength(password: str) -> Dict:
    """Evaluate password strength and return score and rating."""
    score = 0
    feedback = []

    length = len(password)

    # Length score (up to 40 points)
    if length >= 16:
        score += 40
    elif length >= 12:
        score += 30
    elif length >= 8:
        score += 20
    else:
        feedback.append("Password is too short")

    # Character variety (up to 40 points)
    if any(c.islower() for c in password):
        score += 10
    else:
        feedback.append("Add lowercase letters")

    if any(c.isupper() for c in password):
        score += 10
    else:
        feedback.append("Add uppercase letters")

    if any(c.isdigit() for c in password):
        score += 10
    else:
        feedback.append("Add numbers")

    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 10
    else:
        feedback.append("Add special characters")

    # Entropy calculation
    pool_size = 0
    if any(c.islower() for c in password):
        pool_size += 26
    if any(c.isupper() for c in password):
        pool_size += 26
    if any(c.isdigit() for c in password):
        pool_size += 10
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        pool_size += 32

    entropy_bits = length * math.log2(pool_size) if pool_size > 0 else 0

    # Rating
    if score >= 80:
        rating = "Very Strong"
    elif score >= 60:
        rating = "Strong"
    elif score >= 40:
        rating = "Medium"
    elif score >= 20:
        rating = "Weak"
    else:
        rating = "Very Weak"

    return {
        "score": score,
        "rating": rating,
        "entropy_bits": round(entropy_bits, 1),
        "feedback": feedback,
    }
