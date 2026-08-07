import pathlib as pl
import pandas as pd

class MetricsCalculator():
    
    def calculate_metric(self, df: pd.DataFrame) -> pd.DataFrame:
    
        metrics = {
            "Starting_value" : df["Total_value"].iloc[0],
            "Ending_value" : df["Total_value"].iloc[-1],
            "Cumulative_return%" : (df["Total_value"].iloc[-1] / df["Total_value"].iloc[0] - 1) * 100,
            "Daily_volatility%" : df["Portfolio_return_1d%"].std(),
            "Annualized_volatility%" : df["Portfolio_return_1d%"].std() * (252 ** 0.5),
            "Sharpe_ratio" : df["Portfolio_return_1d%"].mean() / df["Portfolio_return_1d%"].std() * (252 ** 0.5),
            "Max_drawdown%" : (df["Total_value"] / df["Total_value"].cummax() - 1).min() * 100,
            "Number_of_trades": int(df["Trade"].abs().sum()),
            "Days_invested%": (df["Signal"].mean() * 100)
        }
    
        metrics_df = pd.DataFrame([metrics])
        
        return metrics_df
    