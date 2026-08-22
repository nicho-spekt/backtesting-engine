from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    
    execution_delay = 1
    
    @abstractmethod
    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def generateFeatures(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
    
    @classmethod
    def validateParameters(cls, params) -> bool:
        pass