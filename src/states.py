import time
from abc import ABC, abstractmethod
from typing import Self


class ProxyState(ABC):
    """
    Base class for states to use.
    """

    @property
    @abstractmethod
    def value(self) -> int:
        """
        Change to __ method?
        :return: integer value based on which bearer of this state can be evaluated.
        """
        ...

    def self_check(self) -> Self:
        """
        Method which is run every time the state is being checked.
        In a common case just returns itself. But can be used to implement
        dynamic transitions to other states or run whatever needed logic.
        :return: A state instance which will be assigned to the bearer of this state
        """
        return self

    def change_to(self, new_state: Self) -> Self:
        """
        Method which is run every time when the new state is being assigned
        to the bearer of this state. In a common case just returns the new state.
        But can be used to implement dynamic transitions ot other states or run whatever
        needed logic.
        :param new_state: A state instance supposed to be assigned to the bearer of this state
        :return: An actual state that will be assigned to the bearer of this state.
        """
        return new_state


# Bellow is default set of states to use:
class Pristine(ProxyState):
    """
    Default state of brand-new instance ready to use
    """

    @property
    def value(self) -> int:
        return 0


class Ready(ProxyState):
    """
    Assigned state of instance ready to use
    """

    @property
    def value(self) -> int:
        return 100


class Issued(ProxyState):
    """
    State of instance that is being used and not available at this moment.
    """

    @property
    def value(self) -> int:
        return 200


class Exhausted(ProxyState):
    """
    State of instance that is not available at this moment. It was
    used and needs time to recover.
    """

    def __init__(self, timeout: int) -> None:
        self.recovery_time = time.time() + timeout

    @property
    def value(self) -> int:
        return 300

    def self_check(self) -> Self:
        return self if self.recovery_time > time.time() else Ready()


class Quarantined(ProxyState):
    """
    State of an instance that is suspect in some failing behavior
    and needs to be put aside for some time
    """

    def __init__(self, timeout: int) -> None:
        self.recovery_time = time.time() + timeout

    @property
    def value(self) -> int:
        return 100 if self.recovery_time > time.time() else 400

    def change_to(self, new_state: ProxyState) -> ProxyState:
        if isinstance(new_state, Quarantined):
            return Broken()
        else:
            return super().change_to(new_state)


class Broken(ProxyState):

    @property
    def value(self) -> int:
        return 500
