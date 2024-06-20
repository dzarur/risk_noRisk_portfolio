import json
import pandas as pd
from glob import glob

with open('config.json', 'r') as file:
    config = json.load(file)
wanted_CIK = config["index"]
top_risk = config['exclude_top_risk']
duration = config['duration']
CIK_path = f"./data/indexes/{wanted_CIK}.csv" # index name insread of wanted_CIK // file_name = "{date_str}" // file_name.format(date_str=[some_parameter / value])

CIKs = pd.read_csv(CIK_path) # relavant companies to analyze from all companies in stock_price

stock_data_paths = glob('./data/stock_prices/*.csv')
lst_dfs_stock_prices = []
for path in stock_data_paths:
    df_stock_price_per_date = pd.read_csv(path, parse_dates=['date']) #maybe date is unnecessary
    lst_dfs_stock_prices.append(df_stock_price_per_date)
df_stock_prices = pd.concat(lst_dfs_stock_prices, ignore_index=True) 

risk_data_paths= glob('./data/risk_scores/*.csv')
lst_dfs_risk_scores = []
for each in risk_data_paths:
    df = pd.read_csv(each, parse_dates=['date']) #maybe date is unnecessary
    risk_df.append(df)
risk_df = pd.concat(risk_df, ignore_index=True)

market_cap_data = glob('./data/market_cap/*.csv')
market_cap_df = []
for each in market_cap_data:
    df = pd.read_csv(each, parse_dates=['date']) #maybe date is unnecessary
    market_cap_df.append(df)
market_cap_df = pd.concat(market_cap_df, ignore_index=True)

relevant_risk_scores = risk_df[risk_df['CIK'].isin(CIKs['CIK'])]
relevant_stock_prices = stock_df[stock_df['CIK'].isin(CIKs['CIK'])]
relevant_market_cap = market_cap_df[market_cap_df['CIK'].isin(CIKs['CIK'])]

top_risk_scores = relevant_risk_scores.sort_values(by='risk_score', ascending=False).head(top_risk)
top_risk_stock_prices = relevant_stock_prices[relevant_stock_prices.isin(top_risk_scores)]
top_risk_market_cap = relevant_market_cap[relevant_market_cap.isin(top_risk_scores)]

risk_scores_without_most_risky = relevant_risk_scores[~relevant_risk_scores.isin(top_risk_scores)]
stock_prices_without_most_risky = relevant_stock_prices[~relevant_stock_prices.isin(top_risk_stock_prices)]
market_cap_without_most_risky = relevant_market_cap[~relevant_market_cap.isin(top_risk_market_cap)]


def stock_price_change_percent(first, second):
    return (second-first)/first

def weight(company_market_cap, portfolio_total_market_cap):
    return company_market_cap/portfolio_total_market_cap

def porftolio_price_change_contribution(weight, stock_price_change_percent):
    return weight*stock_price_change_percent



def entire_portfolio():
    company_market_cap = 
    portfolio_total_market_cap = relevant_market_cap['market_cap_at_prediction_date'].sum()

    stock_price_at_prediction_date = 
    stock_price_at_end_of_period_date = 
    stock_price_change = (stock_price_at_end_of_period_date - stock_price_at_prediction_date) / stock_price_at_prediction_date
    
    weight = company_market_cap/portfolio_total_market_cap
    portfolio_price_change_contribution = weight*stock_price_change

def index_portfolio_excluding_riskiest():
    company_market_cap = 
    portfolio_total_market_cap = market_cap_without_most_risky['market_cap_at_prediction_date'].sum()

    stock_price_at_prediction_date = 
    stock_price_at_end_of_period_date = 
    stock_price_change = (stock_price_at_end_of_period_date - stock_price_at_prediction_date) / stock_price_at_prediction_date

    weight = company_market_cap/portfolio_total_market_cap
    portfolio_price_change_contribution = weight*stock_price_change

def index_portfolio_riskiest_only():
    company_market_cap = 
    portfolio_total_market_cap = top_risk_market_cap['market_cap_at_prediction_date'].sum()

    stock_price_at_prediction_date = 
    stock_price_at_end_of_period_date = 
    stock_price_change = (stock_price_at_end_of_period_date - stock_price_at_prediction_date) / stock_price_at_prediction_date

    weight = company_market_cap/portfolio_total_market_cap
    portfolio_price_change_contribution = weight*stock_price_change