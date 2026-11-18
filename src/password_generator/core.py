"""
Core password generation and strength checking logic.
"""

import math
import secrets
import string
from typing import Dict, List, Sequence, Tuple

# The symbol alphabet actually sampled by generate_password. Strength estimates
# must use this same set; string.punctuation has 32 characters and is not it.
SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
AMBIGUOUS = "Il1O0"


def _validated_pools(
    length: int = 16,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> Tuple[List[str], str]:
    """Return the enabled pools and the joined alphabet they sample from.

    Raises the same TypeError and ValueError as generate_password, so callers
    that produce zero passwords still reject impossible options.
    """
    if isinstance(length, bool) or not isinstance(length, int):
        raise TypeError("Password length must be an integer")

    pools = []

    # Concatenation order is the alphabet secrets.choice samples from.
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append(SYMBOLS)

    if exclude_ambiguous:
        pools = ["".join(c for c in pool if c not in AMBIGUOUS) for pool in pools]

    if not pools:
        raise ValueError("At least one character type must be enabled")

    if length < len(pools):
        raise ValueError(
            "Password length must be at least the number of enabled character types "
            f"({len(pools)})"
        )

    return pools, "".join(pools)


def _draw_password(pools: Sequence[str], alphabet: str, length: int) -> str:
    """Sample until every enabled pool appears at least once."""
    # Rejection sampling keeps all passwords satisfying the category rules
    # equally likely, without a predictable PRNG or a biased seed-and-shuffle.
    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if all(any(c in pool for c in password) for pool in pools):
            return password


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
    pools, alphabet = _validated_pools(
        length=length,
        use_upper=use_upper,
        use_lower=use_lower,
        use_digits=use_digits,
        use_symbols=use_symbols,
        exclude_ambiguous=exclude_ambiguous,
    )
    return _draw_password(pools, alphabet, length)


def batch_generate(
    count: int = 10,
    length: int = 16,
    **kwargs,
) -> List[str]:
    """Generate multiple passwords; count must be a non-negative integer.

    Generation options are validated even when count is zero, so impossible
    lengths and empty alphabets raise instead of returning an empty list.
    """
    if isinstance(count, bool) or not isinstance(count, int):
        raise TypeError("Password count must be an integer")
    if count < 0:
        raise ValueError("Password count must be non-negative")
    pools, alphabet = _validated_pools(length=length, **kwargs)
    return [_draw_password(pools, alphabet, length) for _ in range(count)]


def evaluate_password_strength(password: str) -> Dict:
    """Evaluate password strength and return score, rating, and entropy.

    ``password`` must be a string. Entropy is a rough character-pool estimate:
    ASCII letters and digits contribute 26, 26, and 10. Special characters
    contribute this generator's symbol alphabet, expanded by any other
    non-alphanumeric characters in the password.
    """
    if not isinstance(password, str):
        raise TypeError("Password must be a string")

    score = 0
    feedback = []

    length = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    # Any non-alphanumeric character is a special, not only SYMBOLS. The
    # checker is used on passwords this tool did not generate.
    specials = {c for c in password if not c.isalnum()}

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
    if has_lower:
        score += 10
    else:
        feedback.append("Add lowercase letters")

    if has_upper:
        score += 10
    else:
        feedback.append("Add uppercase letters")

    if has_digit:
        score += 10
    else:
        feedback.append("Add numbers")

    if specials:
        score += 10
    else:
        feedback.append("Add special characters")

    pool_size = 0
    if has_lower:
        pool_size += 26
    if has_upper:
        pool_size += 26
    if has_digit:
        pool_size += 10
    if specials:
        pool_size += len(set(SYMBOLS) | specials)

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
