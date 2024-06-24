import numpy as np
import pandas as pd
from datetime import datetime 

with open('config.json', 'r') as file:
    config = json.load(file)
index = config["index"]
top_risk = config['exclude_top_risk']
duration = config['duration']
start_date = config['start_date']
end_date = config['end_date']
cik_path = "./data/indexes/{index}/{date}.csv".format(index = index, date = start_date)
ciks = pd.read_csv(cik_path)
lst_zero_stock_price = []

df_stock_prices_at_prediction_date = pd.read_csv("./data/stock_prices/{date}.csv".format(date = start_date))
df_stock_prices_at_end_of_period = pd.read_csv("./data/stock_prices/{date}.csv".format(date = end_date))
df_market_cap = pd.read_csv("./data/market_cap/{date}.csv".format(date = start_date))
df_risk_scores = pd.read_csv("./data/risk_scores/{date}.csv".format(date = start_date))

df_stock_prices_at_prediction_date = df_stock_prices_at_prediction_date[df_stock_prices_at_prediction_date['CIK'].isin(ciks['CIK'])].set_index('CIK')
df_stock_prices_at_end_of_period = df_stock_prices_at_end_of_period[df_stock_prices_at_end_of_period['CIK'].isin(ciks['CIK'])].set_index('CIK')
df_market_cap = df_market_cap[df_market_cap['CIK'].isin(ciks['CIK'])].set_index('CIK')
df_market_cap = df_market_cap[df_market_cap['CIK'].isin(ciks['CIK'])].set_index('CIK')
df_risk_scores = df_risk_scores[df_risk_scores['CIK'].isin(ciks['CIK'])].set_index('CIK')

df_stock_prices_at_prediction_date['stock_price_at_prediction_date'] = df_stock_prices_at_prediction_date['stock_price_at_prediction_date'].where(df_stock_prices_at_prediction_date['stock_price_at_prediction_date'] != 0, other=pd.NA)
df_stock_prices_at_end_of_period['stock_price_at_prediction_date'] = df_stock_prices_at_end_of_period['stock_price_at_prediction_date'].where(df_stock_prices_at_end_of_period['stock_price_at_prediction_date'] != 0, other=pd.NA)

df_portfolio = pd.concat([df_stock_prices_at_prediction_date, df_stock_prices_at_end_of_period, df_market_cap, df_risk_scores], axis=1)

market_cap_threshold = 30

(df_portfolio
.assign(stock_pct_change = df_portfolio.eval('(stock_prices_at_end_of_period - stock_price_at_prediction_date)/stock_price_at_prediction_date'),
        belong_to_index = df_portfolio.index.isin(ciks),
        )
.query('belong_to_index & (market_cap > @market_cap_threshold)')
.assign(weight = lambda df: df.eval('market_cap / market_cap.sum()'))
.assign(pct_change_contribution = lambda df: df.eval('stock_pct_change * weight'))
)

df_most_risky_portfolio = df_portfolio.nlargest(top_risk, 'risk_score')
df_excluding_most_risky = df_portfolio[~df_portfolio.index.isin(df_portfolio.index)]


#_________________________________________________________________________________________________________________

df_stock_prices_at_prediction_date = pd.DataFrame({'stock_price_at_prediction_date': np.arange(2, 8)}, index=[20, 1750, 50, 70, 10, 30])
df_stock_prices_at_end_of_period = pd.DataFrame({'stock_prices_at_end_of_period': np.repeat(2, 6)}, index=[10, 30, 50, 70, 20, 1750])
df_market_cap = pd.DataFrame({'market_cap': np.arange(0, 6) * 10}, index=[10, 30, 50, 70, 20, 1750])
lst_index_ciks = [50, 1750]

df_stock_prices_at_end_of_period.loc[30, 'stock_prices_at_end_of_period'] = np.nan

df_stock_prices = pd.concat([df_stock_prices_at_prediction_date, df_stock_prices_at_end_of_period, df_market_cap], axis=1)
df_stock_prices


market_cap_threshold = 30
# df_stock_prices =\
(df_stock_prices
.assign(stock_pct_change = df_stock_prices.eval('(stock_prices_at_end_of_period - stock_price_at_prediction_date)/stock_price_at_prediction_date'),
        belong_to_index = df_stock_prices.index.isin(lst_index_ciks),
        )
.query('belong_to_index & (market_cap > @market_cap_threshold)')
.assign(weight = lambda df: df.eval('market_cap / market_cap.sum()'))
.assign(pct_change_contribution = lambda df: df.eval('stock_pct_change * weight'))
# .pct_change_contribustion
# .sum()
)

lst_dates_portfolio_pct_changes = []
for date_str in dates_strs:
    # creating the record information
    date_portfolios_changes ={
        'date': date_str,
        'index portfolio': 50,
        'index safest only portfolio': -50,
        'index riskiest only portfolio': 30,
        }
    lst_dates_portfolio_pct_changes.append(date_portfolios_changes)