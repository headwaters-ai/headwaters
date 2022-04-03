import pytest

from src.headwaters.stream import Stream
from src.headwaters.source import Source

def test_empty_call_raises():
    """check that instantiating an Stream with no argument raises
    a TypeError
    """
    with pytest.raises(TypeError):
        Stream()

def test_wrong_domain_type_raises():
    """check that the source argument is an object of type Source"""
    with pytest.raises(TypeError):
        Stream('source', 'sio')