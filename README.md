# Password Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

## 中文摘要

这是一个命令行密码生成器，随机源来自操作系统（Python `secrets`）。可以指定长度、大小写、数字和符号，也可以去掉易混淆字符 `Il1O0`，并一次生成多条密码。`check` 用字符种类给出粗略强度分数和熵估计，不能发现常见口令、重复使用或已泄露的密码。下面是英文说明。

A small command-line and Python library for creating passwords and estimating their strength. Passwords are drawn with `secrets`, so each character comes from the operating system's cryptographic random source. Every enabled character category appears at least once.

## Features

- **Secure generation** — OS-backed randomness through Python's `secrets` module
- **Customizable** — length, character types, and optional exclusion of ambiguous characters
- **Strength check** — a basic score plus an estimated entropy from the character pools in the password
- **Batch mode** — generate several passwords with the same character rules as a single password
- **Two commands** — `password-generator` and the shorter `passgen`

## Installation

Requires Python 3.8 or newer.

```bash
git clone https://github.com/Master-626/password-generator.git
cd password-generator
python -m pip install .
```

To work on the code, install the test and lint tools as well:

```bash
python -m pip install -e ".[dev]"
```

## Usage

### Generate one password

```bash
# Default 16-character password
password-generator generate

# 24 characters, no symbols
password-generator generate --length 24 --no-symbols

# Drop ambiguous characters (Il1O0)
passgen generate --exclude-ambiguous
```

Every enabled category appears at least once. The length must be at least the number of enabled categories (4 by default: lowercase, uppercase, digits, and symbols). Ambiguous-character exclusion applies to every character in the password.

### Generate several passwords

`batch` takes the same character options as `generate`.

```bash
# 10 passwords, the default
password-generator batch --count 10 --length 20

# Digits only
password-generator batch --count 5 --length 8 --no-upper --no-lower --no-symbols

# Easier to read aloud
password-generator batch --count 5 --length 20 --no-symbols --exclude-ambiguous
```

`--count 0` is allowed. The command reports that zero passwords were generated, and the Python API returns an empty list. The length and character options are still checked.

### Check a password

```bash
password-generator check --password "example-only"
```

Use an example value for this command. Command-line arguments can be retained in shell history or visible in process listings. Do not pass a real account password on a shared computer.

## Options

Alphabet used when the matching category is enabled:

| Category | Characters | Size |
| --- | --- | --- |
| Lowercase | `a-z` | 26 |
| Uppercase | `A-Z` | 26 |
| Digits | `0-9` | 10 |
| Symbols | 26 characters, listed below | 26 |

```text
!@#$%^&*()_+-=[]{}|;:,.<>?
```

Ambiguous characters removed by `--exclude-ambiguous`: `I`, `l`, `1`, `O`, and `0`.

### `generate`

| Option | Short | Default | Meaning |
| --- | --- | --- | --- |
| `--length` | `-l` | `16` | Password length (integer ≥ 1, and at least the number of enabled categories) |
| `--no-upper` | | off | Exclude uppercase letters |
| `--no-lower` | | off | Exclude lowercase letters |
| `--no-digits` | | off | Exclude digits |
| `--no-symbols` | | off | Exclude symbols |
| `--exclude-ambiguous` | | off | Remove `Il1O0` from every enabled category |

### `batch`

| Option | Short | Default | Meaning |
| --- | --- | --- | --- |
| `--count` | `-n` | `10` | How many passwords to generate (integer ≥ 0) |
| `--length` | `-l` | `16` | Same length rule as `generate` |
| `--no-upper`, `--no-lower`, `--no-digits`, `--no-symbols`, `--exclude-ambiguous` | | off | Same character rules as `generate` |

### `check`

| Option | Short | Meaning |
| --- | --- | --- |
| `--password` | `-p` | Password to score. Required. |

`--version` and `--help` are available on the top-level command and on `passgen`.

## Security notes

- Passwords are drawn with `secrets.choice`, which uses the operating system's cryptographic random source. Candidates missing an enabled category are rejected, so valid passwords are sampled uniformly without a seeded PRNG.
- Use long, unique passwords and a trusted password manager. Selecting fewer character categories or a very short length reduces the available combinations.
- The strength score and `entropy_bits` are rough character-pool estimates, not a measurement of a password's actual unpredictability. They do not detect common passwords, reused passwords, dictionary words, or breached credentials.
- A symbol in the password contributes the 26-character symbol alphabet above. Any other non-alphanumeric character (such as `~`, `/`, quotes, or a space) counts as a special character and is added to that pool. The estimate does not shrink the pool when `--exclude-ambiguous` was used, and it is a poor fit for passwords made only of non-ASCII letters.
- `entropy_bits` is `length * log2(pool)` rounded to one decimal place. It ignores the "at least one character from each category" rule, so it slightly overstates passwords this tool just generated.
- Generated passwords are displayed in your terminal. Be mindful of terminal logs, scrollback, screen sharing, and who can view your screen.

## Python API

```python
from password_generator import generate_password, batch_generate, evaluate_password_strength

pwd = generate_password(length=20, use_symbols=True, exclude_ambiguous=True)

passwords = batch_generate(count=5, length=16, use_symbols=False)

result = evaluate_password_strength("example-only")
print(f"Strength: {result['rating']}, Score: {result['score']}/100")
print(result["entropy_bits"], result["feedback"])
```

`length` must be an integer and fit all selected categories. `count` must be a non-negative integer. `count=0` returns an empty list after those options are validated. `evaluate_password_strength` requires a string. Invalid types and unknown keyword arguments raise `TypeError`. Impossible lengths, negative counts, or no enabled categories raise `ValueError`.

The result dictionary contains `score` (0–80), `rating` (`Very Weak`, `Weak`, `Medium`, `Strong`, `Very Strong`), `entropy_bits`, and `feedback`.

## Testing

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

GitHub Actions runs Ruff and pytest on Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, and 3.14. Python 3.8 uses the Ubuntu 22.04 runner because that version is not published for the current Ubuntu image.

## License

MIT License
