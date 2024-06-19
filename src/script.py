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

try:
    CIKs = pd.read_csv(CIK_path) # relavant companies to analyze from all companies in stock_price
except FileNotFoundError:
    raise FileNotFoundError(f"File '{CIK_path}' not found.")

stock_data = glob.glob('./data/stock_prices/*.csv')
stock_df = []
for each in stock_data:
    df = pd.read_csv(each, parse_dates=['date']) 
    stock_df.append(df)
stock_df = pd.concat(stock_df, ignore_index=True)

# risk_data= glob.glob('./data/risk_scores/*.csv')
# risk_df = []
# for each in risk_data:
#     df = pd.read_csv(each, parse_dates=['date']) 
#     risk_df.append(df)
# risk_df = pd.concat(risk_df, ignore_index=True)

# market_cap_data = glob.glob('./data/market_cap/*.csv')
# market_cap_df = []
# for each in market_cap_data:
#     df = pd.read_csv(each, parse_dates=['date']) 
#     market_cap_df.append(df)
# market_cap_df = pd.concat(market_cap_risk, ignore_index=True)


def relevant_companies():
    relevant_stock_df = stock_df[stock_df['CIK'].isin(CIKs['CIK'])]
    # relevant_risk_df = risk_df[risk_df['CIK']].isin(CIKs['CIK'])
    # relevant_market_cap_df = market_cap_df[market_cap_df['CIK']].isin(CIKs['CIK'])

def stock_price_change_percent(first, second):
    return (second-first)/first

def weight(company_market_cap, portfolio_total_market_cap):
    return company_market_cap/portfolio_total_market_cap

def porftolio_price_change_contribution(weight, stock_price_change_percent):
    return weight*stock_price_change_percent




def entire_portfolio():
    pass

def index_portfolio_excluding_riskiest():
    pass

def index_portfolio_riskiest_only():
    pass