import pandas as pd
import metrics_cpp

class MetricsCalculator:
    
    PERIODS_PER_YEAR = {
        "1d": 252,
        "1wk": 52,
        "1mo": 12,
    }

    def calculateMetrics(self, df: pd.DataFrame, interval) -> pd.DataFrame:

        if interval not in self.PERIODS_PER_YEAR:
            raise ValueError(
                f"Unsupported interval: {interval}"
            )

        annualization_factor = self.PERIODS_PER_YEAR[interval]

        returns = df["Portfolio_return_period"].astype(float).tolist()
        portfolio_values = (df["Total_value"]).astype(float).tolist()
        
        cpp_metrics = metrics_cpp.calculateAll(returns, portfolio_values, annualization_factor)

        metrics = {
            "Starting_value":
                df["Total_value"].iloc[0],

            "Ending_value":
                df["Total_value"].iloc[-1],

            "Cumulative_return":
                cpp_metrics.cumulative_return,

            "Period_volatility":
                cpp_metrics.period_volatility,

            "Annualized_volatility":
                cpp_metrics.annualized_volatility,

            "Sharpe_ratio":
                cpp_metrics.sharpe_ratio,

            "Max_drawdown":
                cpp_metrics.max_drawdown,

            "Number_of_trades":
                int(df["Trade_execution"].abs().sum()),

            "Time_invested":
                df["Signal"].mean(),
        }

        return pd.DataFrame([metrics])