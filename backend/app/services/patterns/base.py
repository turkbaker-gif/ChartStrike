from abc import ABC, abstractmethod


class BasePattern(ABC):

    name: str

    timeframe: str

    @abstractmethod
    def evaluate(self, symbol, features):
        pass