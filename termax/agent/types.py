from abc import ABC, abstractmethod


class Model(ABC):

    def __init__(self):
        self.model_type = None

    @abstractmethod
    def to_command(self, prompt, text):
        pass

    @abstractmethod
    def to_description(self, prompt, command):
        pass
