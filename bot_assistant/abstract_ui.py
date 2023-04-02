from abc import ABC, abstractmethod

class UI(ABC):
    @abstractmethod
    def display_help(self):
        pass

    @abstractmethod
    def greeting(self):
        pass

    @abstractmethod
    def goodbye(self):
        pass

