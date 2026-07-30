from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def plot_portfolio(output_file="data/results/portfolio_plot.png", *series):
    plt.figure(figsize=(12, 6))

    for input_file, label, color in series:
        df = pd.read_csv(input_file, index_col=0, parse_dates=[0])
        plt.plot(df.index, df["Total_value"], label=label, color=color)

    plt.title("Portfolio Value Over Time")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid()

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_file)
    plt.close()

    print(f"Portfolio plot saved to {output_file}")
    
plot_portfolio(
        "data/results/portfolio_plot.png",
    ("data/results/VGT_buy_hold_portfolio.csv", "VGT Buy & Hold", "green"),
    ("data/results/VGT_ma_crossover_portfolio.csv", "MA Crossover Strategy", "blue")
)