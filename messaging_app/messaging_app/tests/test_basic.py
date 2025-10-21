# test_basic.py

def test_addition():
    """Simple sanity test for Jenkins CI/CD pipeline."""
    a = 2
    b = 3
    result = a + b
    assert result == 5, "Addition test failed!"


def test_uppercase():
    """Check that strings convert properly to uppercase."""
    word = "messaging"
    assert word.upper() == "MESSAGING"