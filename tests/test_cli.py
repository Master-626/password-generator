"""CLI validation and literal password output regressions."""

import importlib
import re
from unittest.mock import patch

import pytest
from click.testing import CliRunner

cli = importlib.import_module("password_generator.cli")


@pytest.mark.parametrize("arguments", [
    ["generate", "--length", "0"],
    ["generate", "--length", "-1"],
    ["generate", "--length", "3"],
    ["generate", "--no-upper", "--no-lower", "--no-digits", "--no-symbols"],
    ["batch", "--length", "3"],
    ["batch", "--count", "-1"],
])
def test_invalid_options_produce_clean_cli_errors(arguments):
    result = CliRunner().invoke(cli.main, arguments)
    assert result.exit_code != 0
    assert "Error:" in result.output
    assert "Traceback" not in result.output
    assert "Generated" not in result.output


def test_single_category_allows_a_one_character_password():
    result = CliRunner().invoke(cli.main, [
        "generate", "--length", "1", "--no-upper", "--no-lower", "--no-symbols",
    ])
    assert result.exit_code == 0, result.output
    assert "Generated Password:" in result.output


@pytest.mark.parametrize("password", ["[red]aA2!", ":joy:aA2!", "aA2!" * 40])
def test_generate_preserves_literal_password(password):
    with patch.object(cli, "generate_password", return_value=password):
        result = CliRunner().invoke(cli.main, ["generate"])
    assert result.exit_code == 0, result.output
    assert password in result.output


@pytest.mark.parametrize("password", ["[red]aA2!", ":joy:aA2!", "aA2!" * 40])
def test_batch_preserves_literal_password(password):
    with patch.object(cli, "batch_generate", return_value=[password]):
        result = CliRunner().invoke(cli.main, ["batch", "--count", "1"])
    assert result.exit_code == 0, result.output
    assert password in result.output


def test_empty_batch():
    result = CliRunner().invoke(cli.main, ["batch", "--count", "0"])
    assert result.exit_code == 0, result.output
    assert "Generated 0 passwords" in result.output


def test_check_remains_available():
    result = CliRunner().invoke(cli.main, ["check", "--password", "example-only"])
    assert result.exit_code == 0, result.output
    assert "Password Strength Check" in result.output


def test_check_reports_symbol_entropy_from_the_generator_alphabet():
    result = CliRunner().invoke(cli.main, ["check", "--password", "!"])
    assert result.exit_code == 0, result.output
    assert "4.7 bits" in result.output
    assert "Add special characters" not in result.output


def test_check_counts_characters_outside_the_symbol_alphabet():
    result = CliRunner().invoke(cli.main, ["check", "--password", "~"])
    assert result.exit_code == 0, result.output
    assert "4.8 bits" in result.output
    assert "Add special characters" not in result.output


def test_batch_defaults_match_generate_character_options():
    with patch.object(cli, "batch_generate", return_value=["a"]) as batch:
        result = CliRunner().invoke(cli.main, ["batch", "--count", "1", "--length", "8"])
    assert result.exit_code == 0, result.output
    batch.assert_called_once_with(
        count=1,
        length=8,
        use_upper=True,
        use_lower=True,
        use_digits=True,
        use_symbols=True,
        exclude_ambiguous=False,
    )


def test_batch_forwards_character_options():
    with patch.object(cli, "batch_generate", return_value=["a"]) as batch:
        result = CliRunner().invoke(
            cli.main,
            [
                "batch",
                "--count",
                "2",
                "--length",
                "12",
                "--no-upper",
                "--no-symbols",
                "--exclude-ambiguous",
            ],
        )
    assert result.exit_code == 0, result.output
    batch.assert_called_once_with(
        count=2,
        length=12,
        use_upper=False,
        use_lower=True,
        use_digits=True,
        use_symbols=False,
        exclude_ambiguous=True,
    )


def test_batch_can_limit_character_types():
    result = CliRunner().invoke(
        cli.main,
        [
            "batch",
            "--count",
            "4",
            "--length",
            "6",
            "--no-upper",
            "--no-lower",
            "--no-symbols",
        ],
    )
    assert result.exit_code == 0, result.output
    passwords = re.findall(r"^\s*\d+\. (\d+) - ", result.output, re.MULTILINE)
    assert len(passwords) == 4
    assert all(len(password) == 6 for password in passwords)


def test_batch_exclude_ambiguous_omits_confusable_characters():
    result = CliRunner().invoke(
        cli.main,
        ["batch", "--count", "5", "--length", "12", "--no-symbols", "--exclude-ambiguous"],
    )
    assert result.exit_code == 0, result.output
    passwords = re.findall(r"^\s*\d+\. (\S+) - ", result.output, re.MULTILINE)
    assert len(passwords) == 5
    assert all(set(password).isdisjoint("Il1O0") for password in passwords)
    assert all(
        any(char.islower() for char in password)
        and any(char.isupper() for char in password)
        and any(char.isdigit() for char in password)
        for password in passwords
    )


def test_batch_rejects_impossible_options_without_a_traceback():
    result = CliRunner().invoke(
        cli.main,
        ["batch", "--count", "2", "--no-upper", "--no-lower", "--no-digits", "--no-symbols"],
    )
    assert result.exit_code != 0
    assert "Error:" in result.output
    assert "At least one character type" in result.output
    assert "Traceback" not in result.output
    assert "Generated" not in result.output


def test_batch_count_zero_still_validates_length():
    result = CliRunner().invoke(cli.main, ["batch", "--count", "0", "--length", "3"])
    assert result.exit_code != 0
    assert "Error:" in result.output
    assert "Traceback" not in result.output
    assert "Generated" not in result.output
