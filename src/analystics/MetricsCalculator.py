import pathlib as pl
import pandas as pd

class MetricsCalculator():
    
    def calculateMetrics(self, df: pd.DataFrame, interval) -> pd.DataFrame:
        
        periods_per_year = {
            "1d": 252,
            "1wk": 52,
            "1mo": 12,
        }

        if interval not in periods_per_year:
            raise ValueError(f"Unsupported interval: {interval}")

        annualization_factor = periods_per_year[interval]

        returns = df["Portfolio_return_period%"]

        metrics = {
            "Starting_value": df["Total_value"].iloc[0],
            "Ending_value": df["Total_value"].iloc[-1],
            "Cumulative_return%": (df["Total_value"].iloc[-1]/ df["Total_value"].iloc[0]- 1) * 100,
            "Period_volatility%": returns.std(),
            "Annualized_volatility%":returns.std()* (annualization_factor ** 0.5),
            "Sharpe_ratio":returns.mean()/ returns.std()* (annualization_factor ** 0.5),
            "Max_drawdown%": (df["Total_value"]/ df["Total_value"].cummax()- 1).min() * 100,
            "Number_of_trades": int(df["Execution_Trade"].abs().sum()),
            "Days_invested%": df["Signal"].mean() * 100,
        }
    
        metrics_df = pd.DataFrame([metrics])
        
        return metrics_df
    