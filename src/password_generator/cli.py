"""
CLI interface for password-generator.
"""

import click
from rich.console import Console
from rich.text import Text

from .core import generate_password, batch_generate, evaluate_password_strength

console = Console()


@click.group()
@click.version_option()
def main():
    """Password Generator - Secure password generator with strength checking."""
    pass


@main.command()
@click.option("--length", "-l", default=16, type=click.IntRange(min=1), help="Password length")
@click.option("--no-upper", is_flag=True, help="Exclude uppercase letters")
@click.option("--no-lower", is_flag=True, help="Exclude lowercase letters")
@click.option("--no-digits", is_flag=True, help="Exclude digits")
@click.option("--no-symbols", is_flag=True, help="Exclude special symbols")
@click.option("--exclude-ambiguous", is_flag=True, help="Exclude ambiguous characters (Il1O0)")
def generate(length, no_upper, no_lower, no_digits, no_symbols, exclude_ambiguous):
    """Generate a secure password."""
    try:
        pwd = generate_password(
            length=length,
            use_upper=not no_upper,
            use_lower=not no_lower,
            use_digits=not no_digits,
            use_symbols=not no_symbols,
            exclude_ambiguous=exclude_ambiguous,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    console.print(
        Text.assemble("\n🔐 Generated Password: ", (pwd, "bold green"), "\n"),
        soft_wrap=True,
    )

    # Show strength
    result = evaluate_password_strength(pwd)
    console.print(f"Strength: [bold]{result['rating']}[/bold] (Score: {result['score']}/100)")
    console.print(f"Entropy: {result['entropy_bits']} bits")


@main.command()
@click.option("--count", "-n", default=10, type=click.IntRange(min=0), help="Number of passwords to generate")
@click.option("--length", "-l", default=16, type=click.IntRange(min=4), help="Password length (minimum 4)")
def batch(count, length):
    """Generate multiple passwords at once."""
    passwords = batch_generate(count=count, length=length)

    console.print(f"\n🔐 Generated {count} passwords:\n")
    for i, pwd in enumerate(passwords, 1):
        result = evaluate_password_strength(pwd)
        console.print(
            Text.assemble(f"  {i}. ", (pwd, "bold green"), f" - {result['rating']}"),
            soft_wrap=True,
        )


@main.command()
@click.option("--password", "-p", required=True, help="Password to evaluate")
def check(password):
    """Check password strength."""
    result = evaluate_password_strength(password)

    console.print("\n🔍 Password Strength Check:")
    console.print(f"  Rating: [bold]{result['rating']}[/bold]")
    console.print(f"  Score: {result['score']}/100")
    console.print(f"  Entropy: {result['entropy_bits']} bits")

    if result["feedback"]:
        console.print("\n💡 Suggestions:")
        for suggestion in result["feedback"]:
            console.print(f"  - {suggestion}")


if __name__ == "__main__":
    main()
