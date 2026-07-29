import pandas as pd
from pathlib import Path

def backtest_portfolio(
    input_file,
    initial_capital=100000,
    output_file="data/results/portfolio_backtest.csv"
):
    df = pd.read_csv(input_file, index_col=0, parse_dates=[0])

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    cash = initial_capital
    shares = 0
    
    shares = cash // df["Close"].iloc[0]
    cash -= shares * df["Close"].iloc[0]
    
    df["Shares"] = shares
    df["Cash"] = cash

    for row in df.itertuples():
        price = row.Close

        position_value = shares * price
        total_value = cash + position_value

        df.at[row.Index, "Position_value"] = position_value
        df.at[row.Index, "Total_value"] = total_value

        df.at[row.Index, "Portfolio_return"] = (total_value / initial_capital - 1) * 100

    df["Portfolio_return_1d%"] = df["Total_value"].pct_change().fillna(0)*100

    df.to_csv(output_file)

    print(f"Backtest results saved to {output_file}")


backtest_portfolio(
    "data/raw/VGT.csv",
    initial_capital=100000,
    output_file="data/results/VGT_buy_hold_portfolio.csv"
)