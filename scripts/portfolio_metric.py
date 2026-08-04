import pathlib as pl
import pandas as pd

def calculate_metric(
    input_file,
    output_file="data/results/portfolio_metric_bb.csv"
):
    df = pd.read_csv(input_file)
    
    metrics = {
        "Starting_value" : df["Total_value"].iloc[0],
        "Ending_value" : df["Total_value"].iloc[-1],
        "Cumulative_return%" : (df["Total_value"].iloc[-1] / df["Total_value"].iloc[0] - 1) * 100,
        "Daily_volatility&" : df["Portfolio_return_1d%"].std(),
        "Annualized_volatility&" : df["Portfolio_return_1d%"].std() * (252 ** 0.5),
        "Sharpe_ratio" : df["Portfolio_return_1d%"].mean() / df["Portfolio_return_1d%"].std() * (252 ** 0.5),
        "Max_drawdown%" : (df["Total_value"] / df["Total_value"].cummax() - 1).min() * 100
    }
    
    metrics_df = pd.DataFrame([metrics])
    pl.Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(output_file, index=False)
    
calculate_metric(
    "data/results/VGT_bb_portfolio.csv")