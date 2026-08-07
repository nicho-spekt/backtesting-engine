from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    @abstractmethod
    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:
        pass