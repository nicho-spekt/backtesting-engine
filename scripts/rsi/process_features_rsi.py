import pandas as pd
from ta.momentum import RSIIndicator

lower_std_threshold = 30
upper_std_threshold = 70

def process_features(input_file, output_file, period = 14):
    
    df = pd.read_csv(input_file, index_col=0, parse_dates=[0])
    df = df.sort_index()
    df['RSI'] = RSIIndicator(close=df['Close'], window=period).rsi()
    
    df['Signal'] = pd.NA
    
    df.loc[df["RSI"] < lower_std_threshold, "Signal"] = 1
    df.loc[df["RSI"] > upper_std_threshold, "Signal"] = 0
    
    df["Signal"] = df["Signal"].ffill().fillna(0).astype(int)
    df["Trade"] = df["Signal"].diff().fillna(0).astype(int)
    
    df.dropna(inplace=True)
    
    df.to_csv(output_file)
    
process_features("data/raw/VGT.csv", "data/processed/VGT_features_rsi.csv")