import json
import pandas as pd
import glob

with open('config.json', 'r') as file:
    config = json.load(file)
settings = config['settings']
wanted_CIK = settings["index"]
exclude = settings['exclude_top_risk']
duration = settings['duration']
CIK_path = f"./data/indexes/{wanted_CIK}.csv"

# try:
#     CIKs = pd.read_csv(CIK_path) # relavant companies to analyze from all companies in stock_price
# except FileNotFoundError:
#     raise FileNotFoundError(f"File '{CIK_path}' not found.")

stock_data = glob.glob('./data/stock_prices/*.csv')
stock_df = []
for each in stock_data:
    df = pd.read_csv(each, parse_dates=['date']) 
    stock_df.append(df)
stock_df = pd.concat(stock_df, ignore_index=True)

risk_data= glob.glob('./data/risk_scores/*.csv')
risk_df = []
for each in risk_data:
    df = pd.read_csv(each, parse_dates=['date']) 
    stock_df.append(df)
risk_df = pd.concat(risk_df, ignore_index=True)

