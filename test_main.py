import pytest
from main import root

@pytest.mark.asyncio
def test_root():
    result = await root()
    assert result == "Hello Student"

