import pandas as pd

def process_features(input_file, output_file):

    df = pd.read_csv(input_file, index_col=0, parse_dates=[0])
    
    df['Ma_20'] = df['Close'].rolling(20).mean()
    df['Ma_50'] = df['Close'].rolling(50).mean()
    
    df['Signal'] = (df['Ma_20'] > df['Ma_50']).astype(int)
    df['Trade'] = df['Signal'].diff().fillna(0).astype(int)
    df['Holding'] = df['Signal']
    df['Return_1d'] = df['Close'].pct_change().fillna(0)
    
    df.dropna(inplace=True)
    
    df.to_csv(output_file)
    
    print(f"Processed features saved to {output_file}")
    

process_features("data/raw/VGT.csv", "data/processed/VGT_features.csv")