from password_generator.core import generate_password, batch_generate, evaluate_password_strength


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
