"""Regression tests for the password generator's security guarantees."""

import itertools
import string
from unittest.mock import patch

import pytest

from password_generator import batch_generate, generate_password
from password_generator.core import AMBIGUOUS, SYMBOLS

CATEGORIES = (
    ("use_lower", string.ascii_lowercase),
    ("use_upper", string.ascii_uppercase),
    ("use_digits", string.digits),
    ("use_symbols", SYMBOLS),
)
OPTIONS = list(itertools.product((False, True), repeat=4))[1:]


@pytest.mark.parametrize("enabled", OPTIONS)
@pytest.mark.parametrize("exclude_ambiguous", [False, True])
@pytest.mark.parametrize("extra_length", [0, 12])
def test_every_category_combination(enabled, exclude_ambiguous, extra_length):
    options = {name: flag for (name, _), flag in zip(CATEGORIES, enabled)}
    pools = [pool for (_, pool), flag in zip(CATEGORIES, enabled) if flag]
    if exclude_ambiguous:
        pools = ["".join(c for c in pool if c not in AMBIGUOUS) for pool in pools]
    length = len(pools) + extra_length

    password = generate_password(
        length=length, exclude_ambiguous=exclude_ambiguous, **options
    )

    assert len(password) == length
    assert set(password) <= set("".join(pools))
    assert all(any(c in pool for c in password) for pool in pools)


def test_uses_secrets_for_every_character_and_rejects_missing_categories():
    # The first candidate lacks three selected categories; the second is valid.
    with patch("secrets.choice", side_effect=list("aaaaaA2!")) as choice:
        password = generate_password(length=4)

    assert password == "aA2!"
    assert choice.call_count == 8
    expected_pool = string.ascii_lowercase + string.ascii_uppercase + string.digits + SYMBOLS
    assert all(call.args == (expected_pool,) for call in choice.call_args_list)


def test_ambiguous_characters_never_reach_secure_sampler():
    with patch("secrets.choice", side_effect=list("aA2!")) as choice:
        assert generate_password(length=4, exclude_ambiguous=True) == "aA2!"
    assert all(not set(call.args[0]) & set(AMBIGUOUS) for call in choice.call_args_list)


@pytest.mark.parametrize("length", [-10, -1, 0, 1, 2, 3])
def test_rejects_lengths_that_cannot_fit_selected_categories(length):
    with pytest.raises(ValueError, match="length"):
        generate_password(length=length)


@pytest.mark.parametrize("length", [True, False, 1.5, "16", None])
def test_rejects_non_integer_lengths(length):
    with pytest.raises(TypeError, match="integer"):
        generate_password(length=length)


def test_rejects_empty_character_set():
    with pytest.raises(ValueError, match="At least one character type"):
        generate_password(use_upper=False, use_lower=False, use_digits=False, use_symbols=False)


@pytest.mark.parametrize("count", [-1, -10])
def test_rejects_negative_batch_counts(count):
    with pytest.raises(ValueError, match="count"):
        batch_generate(count=count)


@pytest.mark.parametrize("count", [True, False, 1.5, "2", None])
def test_rejects_non_integer_batch_counts(count):
    with pytest.raises(TypeError, match="integer"):
        batch_generate(count=count)


def test_zero_batch_count_is_empty():
    with patch("secrets.choice") as choice:
        assert batch_generate(count=0) == []
    choice.assert_not_called()


def test_zero_batch_count_still_validates_options():
    with pytest.raises(ValueError, match="length"):
        batch_generate(count=0, length=3)
    with pytest.raises(ValueError, match="At least one character type"):
        batch_generate(
            count=0,
            use_upper=False,
            use_lower=False,
            use_digits=False,
            use_symbols=False,
        )
    with pytest.raises(TypeError, match="integer"):
        batch_generate(count=0, length=True)
    with pytest.raises(TypeError):
        batch_generate(count=0, lenght=8)


def test_count_errors_are_reported_before_generation_options():
    with pytest.raises(ValueError, match="count"):
        batch_generate(count=-1, length="bad")
    with pytest.raises(TypeError, match="count"):
        batch_generate(count=1.5, length="bad")


def test_batch_preserves_options():
    passwords = batch_generate(
        count=5, length=10, use_upper=False, use_lower=False,
        use_symbols=False, exclude_ambiguous=True,
    )
    assert len(passwords) == 5
    assert all(len(password) == 10 and set(password) <= set("23456789") for password in passwords)
