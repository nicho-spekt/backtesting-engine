import pandas as pd
from ta.volatility import BollingerBands

def process_features(input_file, output_file, window=20, window_dev=2):
    
    df = pd.read_csv(input_file, index_col=0, parse_dates=[0])
    df = df.sort_index()
    
    indicator_bb = BollingerBands(close=df["Close"], window=window, window_dev=window_dev)
    
    df["BB_Middle"] = indicator_bb.bollinger_mavg()
    df["BB_Upper"] = indicator_bb.bollinger_hband()
    df["BB_Lower"] = indicator_bb.bollinger_lband()
    
    df.loc[df["Close"] < df["BB_Lower"], "Signal"] = 1
    df.loc[df["Close"] > df["BB_Middle"], "Signal"] = 0
    
    df["Signal"] = df["Signal"].ffill().fillna(0).astype(int)
    df["Trade"] = df["Signal"].diff().fillna(0).astype(int)
    
    df.dropna(inplace=True)
    
    df.to_csv(output_file)
    
process_features("data/raw/VGT.csv", "data/processed/VGT_features_bb.csv")
    