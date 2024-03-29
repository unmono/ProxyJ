import warnings
from typing import Protocol, Iterable
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
    name: str

    def get_list(self) -> [Proxy]: ...


service_protocol_error = AttributeError("Service must follow defined protocol")


class NoProxyLeftException(Exception):
    pass


class NoSuchServiceWarning(UserWarning):
    pass


class ProxyJ:

    def __init__(
            self,
            services: ProxyServiceProtocol | Iterable[ProxyServiceProtocol],
            state_value_threshold: int
    ) -> None:
        self._pool: [Proxy] = []
        self._switched_off: dict[str, ProxyServiceProtocol] = {}
        try:
            self._services: dict[str, ProxyServiceProtocol] = {s.name: s for s in services}
        except AttributeError:
            raise service_protocol_error
        except TypeError:
            try:
                self._services[services.name] = services
            except AttributeError:
                raise service_protocol_error
        self._state_threshold: int = state_value_threshold

    def _fill_pool(self) -> None:
        self._pool.clear()
        for s in self._services.values():
            self._pool.extend(s.get_list())

    def get_one(self) -> Proxy:
        pool_length = len(self._pool)
        for i, p in enumerate(self._pool):
            if p.state.value < self._state_threshold:
                if i > pool_length // 3:
                    self._mix_pool()
                return p
        else:
            if pool_length < 1:
                raise NoProxyLeftException("The pool is empty. Check services")
            raise NoProxyLeftException("No proxy available at that moment")

    def add_service(self, service: ProxyServiceProtocol) -> None:
        self._services[service.name] = service
        self._fill_pool()

    def del_service(self, name: str) -> None:
        self._services.pop(name, None)
        self._fill_pool()

    def switch_service_off(self, name: str) -> None:
        try:
            self._switched_off[name] = self._services.pop(name)
        except KeyError:
            if name in self._switched_off:
                warnings.warn(
                    message=f'The service {name} is already switched off',
                    category=NoSuchServiceWarning,
                )
            else:
                warnings.warn(
                    message=f'No such service {name} to switch off. At least at this given point of time.',
                    category=NoSuchServiceWarning,
                )
        else:
            self._fill_pool()

    def switch_service_on(self, name: str) -> None:
        try:
            self._services[name] = self._switched_off.pop(name)
        except KeyError:
            if name in self._services:
                warnings.warn(
                    message=f'The service {name} is already switched on',
                    category=NoSuchServiceWarning,
                )
            else:
                warnings.warn(
                    message=f'No such service {name} to switch on. At least at this given point of time.',
                    category=NoSuchServiceWarning,
                )
        else:
            self._fill_pool()

    def _mix_pool(self) -> None:
        pass
