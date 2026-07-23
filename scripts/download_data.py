import yfinance as yf
import pathlib as pl
import pandas as pd

tickers = ["VGT", "SPY"]
start_date = "2015-01-01"
end_date = "2025-12-31"

output_dir = pl.Path("data/raw")
output_dir.mkdir(parents = True, exist_ok = True)

for ticker in tickers:
    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval="1d",
        auto_adjust=True
    )
    
    if data.empty:
        raise ValueError(f"No data downloaded for {ticker}")
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.index.name = "Date"

    file_path = output_dir / f"{ticker}.csv"
    data.to_csv(file_path)

    print(f"Saved {ticker} data to {file_path}")