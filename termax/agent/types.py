from abc import ABC, abstractmethod


class Model(ABC):
    @abstractmethod
    def to_command(self, request):
        pass
