"""
Core password generation and strength checking logic.
"""

import math
import random
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
    """Generate a secure random password."""
    chars = ""

    if use_lower:
        chars += string.ascii_lowercase
    if use_upper:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if exclude_ambiguous:
        ambiguous = "Il1O0"
        chars = "".join(c for c in chars if c not in ambiguous)

    if not chars:
        raise ValueError("At least one character type must be enabled")

    # Ensure at least one from each selected category
    password_chars = []
    if use_lower:
        password_chars.append(random.choice(string.ascii_lowercase))
    if use_upper:
        password_chars.append(random.choice(string.ascii_uppercase))
    if use_digits:
        password_chars.append(random.choice(string.digits))
    if use_symbols:
        password_chars.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))

    # Fill the rest
    remaining = length - len(password_chars)
    password_chars.extend(random.choice(chars) for _ in range(remaining))

    # Shuffle
    random.shuffle(password_chars)

    return "".join(password_chars[:length])


def batch_generate(
    count: int = 10,
    length: int = 16,
    **kwargs,
) -> List[str]:
    """Generate multiple passwords at once."""
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
