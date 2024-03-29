import warnings
from typing import Protocol, Iterable
from abc import ABC, abstractmethod

from states import ProxyState, ProxyStateDescriptor


class Proxy(ABC):
    state = ProxyStateDescriptor()

    @property
    @abstractmethod
    def ip(self) -> str:
        """
        :return: IP address of a proxy
        """
        ...


class ProxyProviderProtocol(Protocol):
    name: str

    def get_list(self) -> [Proxy]: ...


provider_protocol_error = AttributeError("Provider must follow defined protocol")


class NoProxyLeftException(Exception):
    pass


class NoSuchProviderWarning(UserWarning):
    pass


class ProxyJ:
    """
    Issues proxy instances based on their state.
    Support multiple proxy providers.
    """

    def __init__(
            self,
            providers: ProxyProviderProtocol | Iterable[ProxyProviderProtocol],
            state_value_threshold: int
    ) -> None:
        self._pool: [Proxy] = []
        self._switched_off: dict[str, ProxyProviderProtocol] = {}
        try:
            self._providers: dict[str, ProxyProviderProtocol] = {s.name: s for s in providers}
        except AttributeError:
            raise provider_protocol_error
        except TypeError:
            try:
                self._providers[providers.name] = providers
            except AttributeError:
                raise provider_protocol_error
        self._state_threshold: int = state_value_threshold

    def _fill_pool(self) -> None:
        self._pool.clear()
        for s in self._providers.values():
            self._pool.extend(s.get_list())

    def get_one(self) -> Proxy:
        """
        Issue a single proxy instance.
        :return: ready to use proxy instance
        """
        pool_length = len(self._pool)
        for i, p in enumerate(self._pool):
            if p.state.value < self._state_threshold:
                # Prospective mechanism to refine pool order.
                # It's just how it could look like, but actual implementation has to be
                # well thought out and tested
                if i > pool_length // 3:
                    self._mix_pool()
                return p
        else:
            if pool_length < 1:
                raise NoProxyLeftException("The pool is empty. Check providers")
            raise NoProxyLeftException("No proxy available at that moment")

    def add_provider(self, provider: ProxyProviderProtocol) -> None:
        self._providers[provider.name] = provider
        self._fill_pool()

    def del_provider(self, name: str) -> None:
        self._providers.pop(name, None)
        self._fill_pool()

    def switch_provider_off(self, name: str) -> None:
        try:
            self._switched_off[name] = self._providers.pop(name)
        except KeyError:
            if name in self._switched_off:
                warnings.warn(
                    message=f'The provider {name} is already switched off',
                    category=NoSuchProviderWarning,
                )
            else:
                warnings.warn(
                    message=f'No such provider {name} to switch off. At least at this given point of time.',
                    category=NoSuchProviderWarning,
                )
        else:
            self._fill_pool()

    def switch_provider_on(self, name: str) -> None:
        try:
            self._providers[name] = self._switched_off.pop(name)
        except KeyError:
            if name in self._providers:
                warnings.warn(
                    message=f'The provider {name} is already switched on',
                    category=NoSuchProviderWarning,
                )
            else:
                warnings.warn(
                    message=f'No such provider {name} to switch on. At least at this given point of time.',
                    category=NoSuchProviderWarning,
                )
        else:
            self._fill_pool()

    def _mix_pool(self) -> None:
        """
        Prospective method.
        Reorder instances to be more efficient and prevent usage only of the first part of pool.
        """
        pass
