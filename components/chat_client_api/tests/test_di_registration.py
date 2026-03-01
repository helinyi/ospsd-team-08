# components/chat_client_api/tests/test_di_registration.py

import pytest
from chat_client_api import get_client, register_client_factory


class DummyClient:
    pass


def test_get_client_raises_when_unregistered():
    with pytest.raises(RuntimeError):
        get_client()


def test_register_client_factory():
    def factory():
        return DummyClient()

    register_client_factory(factory)
    client = get_client()
    assert isinstance(client, DummyClient)
