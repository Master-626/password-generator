# Password Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

A secure password generator with strength checking and batch generation support.

## 🌟 Features

- 🔐 **Secure Generation** - Cryptographically secure random passwords
- 🎛️ **Customizable** - Control length, character types, exclude ambiguous chars
- 📊 **Strength Check** - Evaluate password strength with entropy calculation
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

### Batch Generate
```bash
# Generate 10 passwords
password-generator batch --count 10 --length 20
```

### Check Password Strength
```bash
password-generator check --password "MySecurePass123!"
```

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

## 🧪 Testing

```bash
pip install -e ".[dev]"
pytest
```

## 📄 License

MIT License
