"""
password-generator - Secure password generator with strength checking.
"""

from .core import generate_password, batch_generate, evaluate_password_strength

__version__ = "0.1.0"
__all__ = ["generate_password", "batch_generate", "evaluate_password_strength"]
