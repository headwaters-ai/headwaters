import pytest

from src.headwaters.engine import Engine
from src.headwaters.domains import Domain

def test_empty_call_raises():
    """check that instantiating an Engine with no argument raises
    a TypeError
    """
    with pytest.raises(TypeError):
        Engine()

def test_wrong_domain_type_raises():
    """check that the domain argument is an object of type Domain"""
    with pytest.raises(TypeError):
        Engine('domain', 'sio')