from typing import Protocol
from abc import ABC, abstractmethod

from states import ProxyState


class ProxyStateDescriptor:

    def __get__(self, instance, owner):
        try:
            current_state: ProxyState = getattr(instance, '_state')
        except AttributeError:
            raise AttributeError("Instance of proxy class implementation has to have "
                                 "a '_state' attribute initialized before checking. "
                                 "It can be some default state or dynamic logic.")
        try:
            instance._state = current_state.self_check()
        except AttributeError:
            raise AttributeError("Implementation of proxy state class has to have self_check() method.")
        return instance._state

    def __set__(self, instance, value: ProxyState):
        try:
            instance._state = instance._state.change_to(value)
        except AttributeError:
            instance._state = value


class Proxy(ABC):
    state = ProxyStateDescriptor()

    @property
    @abstractmethod
    def ip(self) -> str: ...


class ProxyServiceProtocol(Protocol):

    def get_list(self) -> [Proxy]: ...


class ProxyJ:

    def __init__(self, service: [ProxyServiceProtocol]) -> None:
        self.service = service

    def get_one(self) -> Proxy:
        pass

    def add_service(self, service: ProxyServiceProtocol) -> None:
        pass

    def del_service(self):
        pass

    def switch_service_off(self):
        pass

    def switch_service_on(self):
        pass
