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


class ProxyStateDescriptor:
    """
    Makes possible to run some additional logic while getting and setting states.
    The goal is to make possible to implement some transitional states that manage themselves while
    their owners are, for example, being sorted.
    Example: program can iterate over some instances until it hits one with an appropriate state. At the same
    time there is an instance with some transitional state that supposed to be changed after timeout.
    At the moment its state is checked, its method checks if the timeout is over and changes itself to
    another one, so it can be picked.
    """

    def __get__(self, instance, owner):
        try:
            current_state: ProxyState = getattr(instance, '_state')
        except AttributeError:
            raise AttributeError("Instance of proxy class implementation has to have "
                                 "a '_state' attribute initialized before checking. "
                                 "It can be some default state or dynamic logic.")
        try:
            # .self_check() is a method that supposed to run any additional logic if needed
            # and return desired state based on it. This new state becomes an actual state
            # of instance. In a common case it just returns self and nothing changes.
            instance._state = current_state.self_check()
        except AttributeError:
            raise AttributeError("Implementation of proxy state class has to have self_check() method.")
        return instance._state

    def __set__(self, instance, value: ProxyState):
        try:
            # .change_to() is a method that supposed to alter the setting of states if needed.
            # Let's say that in a common case we want to assign some "Failed" state to instances
            # that don't work in some way. But also we want to have an instance with some exceptional
            # state that goes, say, "Quarantined" when we assign "Failed" to it.
            # This way the logic of user program will be decoupled from any exceptional cases, and they
            # will be managed by states itself.
            instance._state = instance._state.change_to(value)
        except AttributeError:
            # If the state is not set yet, set it.
            instance._state = value


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
