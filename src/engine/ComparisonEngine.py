import pandas as pd
from engine.Backtester import Backtester
from analystics.MetricsCalculator import MetricsCalculator

class ComparisonEngine():
    
    def __init__(self, df:pd.DataFrame, initial_capital = 100000, **kwargs):
        self.df = df.copy().sort_index()
        self.initial_capital = initial_capital
        self.dict_strategies = kwargs
        
    def runStrategies(self):

        strategy_dataframes = {}
        portfolio_results = {}
        comparison_rows = []
        
        metrics_calculator = MetricsCalculator()

        for name, strategy in self.dict_strategies.items():
            strategy_dataframes[name] = strategy.generateSignals(self.df)

        common_start_date = max(
            df.index.min()
            for df in strategy_dataframes.values()
        )

        for name, df in strategy_dataframes.items():

            df = df.loc[common_start_date:].copy()

            previous_signal = df["Signal"].shift(fill_value=0)
            df["Trade"] = (df["Signal"] - previous_signal).astype(int)

            backtester = Backtester(self.initial_capital)
            portfolio_df = backtester.run(df)
            
            portfolio_results[name] = portfolio_df
            
            metrics_df = metrics_calculator.calculateMetrics(portfolio_df)
            
            metrics = {
                "Strategy": name,
                **metrics_df.iloc[0].to_dict()
            }
            
            comparison_rows.append(metrics)

        comparison_df = pd.DataFrame(comparison_rows)
        
        return portfolio_results, comparison_df
            