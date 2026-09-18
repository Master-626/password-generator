"""
CLI interface for password-generator.
"""

import click
from rich.console import Console
from rich.table import Table

from .core import generate_password, batch_generate, evaluate_password_strength

console = Console()


@click.group()
@click.version_option()
def main():
    """Password Generator - Secure password generator with strength checking."""
    pass


@main.command()
@click.option("--length", "-l", default=16, help="Password length")
@click.option("--no-upper", is_flag=True, help="Exclude uppercase letters")
@click.option("--no-lower", is_flag=True, help="Exclude lowercase letters")
@click.option("--no-digits", is_flag=True, help="Exclude digits")
@click.option("--no-symbols", is_flag=True, help="Exclude special symbols")
@click.option("--exclude-ambiguous", is_flag=True, help="Exclude ambiguous characters (Il1O0)")
def generate(length, no_upper, no_lower, no_digits, no_symbols, exclude_ambiguous):
    """Generate a secure password."""
    pwd = generate_password(
        length=length,
        use_upper=not no_upper,
        use_lower=not no_lower,
        use_digits=not no_digits,
        use_symbols=not no_symbols,
        exclude_ambiguous=exclude_ambiguous,
    )

    console.print(f"\n🔐 Generated Password: [bold green]{pwd}[/bold green]\n")

    # Show strength
    result = evaluate_password_strength(pwd)
    console.print(f"Strength: [bold]{result['rating']}[/bold] (Score: {result['score']}/100)")
    console.print(f"Entropy: {result['entropy_bits']} bits")


@main.command()
@click.option("--count", "-n", default=10, help="Number of passwords to generate")
@click.option("--length", "-l", default=16, help="Password length")
def batch(count, length):
    """Generate multiple passwords at once."""
    passwords = batch_generate(count=count, length=length)

    console.print(f"\n🔐 Generated {count} passwords:\n")
    for i, pwd in enumerate(passwords, 1):
        result = evaluate_password_strength(pwd)
        console.print(f"  {i}. [bold green]{pwd}[/bold green] - {result['rating']}")


@main.command()
@click.option("--password", "-p", required=True, help="Password to evaluate")
def check(password):
    """Check password strength."""
    result = evaluate_password_strength(password)

    console.print(f"\n🔍 Password Strength Check:")
    console.print(f"  Rating: [bold]{result['rating']}[/bold]")
    console.print(f"  Score: {result['score']}/100")
    console.print(f"  Entropy: {result['entropy_bits']} bits")

    if result["feedback"]:
        console.print("\n💡 Suggestions:")
        for suggestion in result["feedback"]:
            console.print(f"  - {suggestion}")


if __name__ == "__main__":
    main()
