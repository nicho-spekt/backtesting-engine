from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    
    execution_delay = 1
    
    @abstractmethod
    def generateSignals(self, df: pd.DataFrame) -> pd.DataFrame:
        pass