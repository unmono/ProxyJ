import time
from abc import ABC, abstractmethod
from typing import Self


class ProxyState(ABC):

    @property
    @abstractmethod
    def state_value(self) -> int: ...

    def self_check(self) -> Self:
        return self

    def change_to(self, new_state: Self) -> Self:
        return new_state


class Pristine(ProxyState):

    @property
    def state_value(self) -> int:
        return 0


class Ready(ProxyState):

    @property
    def state_value(self) -> int:
        return 100


class Issued(ProxyState):

    @property
    def state_value(self) -> int:
        return 200


class Exhausted(ProxyState):

    def __init__(self, timeout: int) -> None:
        self.recovery_time = time.time() + timeout

    @property
    def state_value(self) -> int:
        return 300

    def self_check(self) -> Self:
        return self if self.recovery_time > time.time() else Ready()


class Quarantined(ProxyState):

    def __init__(self, timeout: int) -> None:
        self.recovery_time = time.time() + timeout

    @property
    def state_value(self) -> int:
        return 100 if self.recovery_time > time.time() else 400

    def change_to(self, new_state: ProxyState) -> ProxyState:
        if isinstance(new_state, Quarantined):
            return Broken()
        else:
            return super().change_to(new_state)


class Broken(ProxyState):

    @property
    def state_value(self) -> int:
        return 500
