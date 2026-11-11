import math

import pytest

from password_generator.core import (
    SYMBOLS,
    batch_generate,
    evaluate_password_strength,
    generate_password,
)


def test_generate_password_default():
    """Test default password generation."""
    pwd = generate_password()
    assert len(pwd) == 16
    assert any(c.isupper() for c in pwd)
    assert any(c.islower() for c in pwd)
    assert any(c.isdigit() for c in pwd)


def test_generate_password_custom_length():
    """Test custom length password."""
    pwd = generate_password(length=32)
    assert len(pwd) == 32


def test_batch_generate():
    """Test batch password generation."""
    passwords = batch_generate(count=5, length=12)
    assert len(passwords) == 5
    assert all(len(p) == 12 for p in passwords)


def test_evaluate_weak_password():
    """Test weak password evaluation."""
    result = evaluate_password_strength("abc")
    assert result["rating"] in ["Very Weak", "Weak"]
    assert result["score"] < 50


def test_evaluate_strong_password():
    """Test strong password evaluation."""
    result = evaluate_password_strength("K9#vP2!mX9$LqZ8@")
    assert result["rating"] in ["Strong", "Very Strong"]
    assert result["score"] >= 70


@pytest.mark.parametrize(
    ("password", "score", "rating"),
    [
        ("", 0, "Very Weak"),
        ("abc", 10, "Very Weak"),
        ("abcdefgh", 30, "Weak"),
        ("Abcdefg1", 50, "Medium"),
        ("Abcdefg1!", 60, "Strong"),
        ("Abcdefghijk1!xxx", 80, "Very Strong"),
    ],
)
def test_strength_score_bands(password, score, rating):
    result = evaluate_password_strength(password)
    assert result["score"] == score
    assert result["rating"] == rating


def test_symbol_entropy_uses_generator_alphabet():
    """The symbol pool is the 26-character generator alphabet, not punctuation (32)."""
    result = evaluate_password_strength("!")
    alphabet = 26 + 26 + 10 + len(SYMBOLS)
    assert len(SYMBOLS) == 26
    assert result["entropy_bits"] == round(math.log2(len(SYMBOLS)), 1)
    assert result["entropy_bits"] != round(math.log2(32), 1)

    mixed = evaluate_password_strength("aA1!")
    assert mixed["entropy_bits"] == round(4 * math.log2(alphabet), 1)


@pytest.mark.parametrize(
    "password",
    ["MyPass123~", "MyPass123/", "MyPass123'", 'MyPass123"', "MyPass123\\", " " * 8, "~" * 16],
)
def test_non_alphabet_specials_count_as_symbols(password):
    result = evaluate_password_strength(password)
    assert "Add special characters" not in result["feedback"]
    assert result["entropy_bits"] > 0


def test_extra_specials_expand_the_symbol_pool():
    result = evaluate_password_strength("~" * 16)
    pool = len(set(SYMBOLS) | set("~"))
    assert result["score"] == 50
    assert result["rating"] == "Medium"
    assert result["entropy_bits"] == round(16 * math.log2(pool), 1)
    assert result["feedback"] == [
        "Add lowercase letters",
        "Add uppercase letters",
        "Add numbers",
    ]

    checked = evaluate_password_strength("MyPass123~")
    assert checked["score"] == 60
    assert checked["rating"] == "Strong"
    assert "Add special characters" not in checked["feedback"]


def test_empty_password_feedback():
    result = evaluate_password_strength("")
    assert result["entropy_bits"] == 0
    assert result["feedback"] == [
        "Password is too short",
        "Add lowercase letters",
        "Add uppercase letters",
        "Add numbers",
        "Add special characters",
    ]


@pytest.mark.parametrize("password", [None, 123, b"abc", ["a", "b"], ("a",), True])
def test_strength_rejects_non_strings(password):
    with pytest.raises(TypeError, match="string"):
        evaluate_password_strength(password)
