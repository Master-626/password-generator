"""CLI validation and literal password output regressions."""

import importlib
from unittest.mock import patch

from click.testing import CliRunner
import pytest


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
