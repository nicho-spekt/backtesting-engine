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

    for row in df.itertuples():
        price = row.Close
        trade_signal = row.Trade

        if trade_signal == 1:
            shares_to_buy = int(cash // price)
            cash -= shares_to_buy * price
            shares += shares_to_buy

        elif trade_signal == -1:
            cash += shares * price
            shares = 0

        position_value = shares * price
        total_value = cash + position_value

        df.at[row.Index, "Shares"] = shares
        df.at[row.Index, "Cash"] = cash
        df.at[row.Index, "Position_value"] = position_value
        df.at[row.Index, "Total_value"] = total_value

        df.at[row.Index, "Portfolio_return"] = (total_value / initial_capital - 1) * 100

    df["Portfolio_return_1d"] = df["Total_value"].pct_change().fillna(0)

    df.drop(
        columns=["Ma_20", "Ma_50", "Signal", "Holding", "Return_1d"],
        inplace=True,
        errors="ignore"
    )

    df.to_csv(output_file)

    print(f"Backtest results saved to {output_file}")


backtest_portfolio(
    "data/processed/VGT_features.csv",
    initial_capital=100000,
    output_file="data/results/VGT_ma_crossover_portfolio.csv"
)