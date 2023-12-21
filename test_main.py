from main import root

def test_root():
    result = await root()
    assert result == "Hello Student"

