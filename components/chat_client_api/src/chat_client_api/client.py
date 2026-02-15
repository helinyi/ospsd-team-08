from abc import ABC, abstractmethod


class ChatClient(ABC):

    @abstractmethod
    def send_message(self, channel: str, message: str) -> None:
        pass


# for dependency injection
_client_factory = None


def register_client(factory_func):
    global _client_factory
    _client_factory = factory_func


def get_client() -> ChatClient:
    if _client_factory is None:
        raise RuntimeError("No client implementation found!")

    return _client_factory()
