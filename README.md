# Password Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

A secure password generator with strength checking and batch generation support.

## 🌟 Features

- 🔐 **Secure Generation** - OS-backed randomness through Python's `secrets` module
- 🎛️ **Customizable** - Control length, character types, exclude ambiguous chars
- 📊 **Strength Check** - A basic strength heuristic and estimated entropy
- 📦 **Batch Mode** - Generate multiple passwords at once
- 🎨 **Rich Output** - Beautiful colored terminal output

## 📦 Installation

```bash
git clone https://github.com/Master-626/password-generator.git
cd password-generator
pip install .
```

## 🚀 Usage

### Generate a Password
```bash
# Default 16-character password
password-generator generate

# 24-character password without symbols
password-generator generate --length 24 --no-symbols

# Exclude ambiguous characters (Il1O0)
password-generator generate --exclude-ambiguous
```

Every enabled character category appears at least once. The length must be at
least the number of enabled categories (4 by default). Ambiguous-character
exclusion applies to every character in the password.

### Batch Generate
```bash
# Generate 10 passwords
password-generator batch --count 10 --length 20
```

### Check Password Strength
```bash
password-generator check --password "MySecurePass123!"
```

Use an example value for this command: command-line arguments can be retained in
shell history or visible in process listings. Do not pass a real account password
on a shared computer.

## Security Notes

- Passwords are drawn with `secrets.choice`, which uses the operating system's
  cryptographic random source. Candidates missing an enabled category are
  rejected, so valid passwords are sampled uniformly without a seeded PRNG.
- Use long, unique passwords and a trusted password manager. Selecting fewer
  character categories or a very short length reduces the available combinations.
- The strength score and `entropy_bits` are rough character-pool estimates, not a
  measurement of a password's actual unpredictability. They do not detect common
  passwords, reused passwords, dictionary words, or breached credentials.
- Generated passwords are displayed in your terminal. Be mindful of terminal
  logs, scrollback, screen sharing, and who can view your screen.

## 🐍 Python API

```python
from password_generator import generate_password, batch_generate, evaluate_password_strength

# Generate a password
pwd = generate_password(length=20, use_symbols=True)

# Batch generate
passwords = batch_generate(count=5, length=16)

# Check strength
result = evaluate_password_strength("MyPassword123!")
print(f"Strength: {result['rating']}, Score: {result['score']}/100")
```

`length` must be an integer and fit all selected categories. `count` must be a
non-negative integer; `count=0` returns an empty list. Invalid types raise
`TypeError`, and impossible lengths, negative counts, or no enabled categories
raise `ValueError`.

## 🧪 Testing

```bash
pip install -e ".[dev]"
pytest
```

## 📄 License

MIT License
