import numpy as np
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, Tuple

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

df_stock_prices_at_prediction_date = (pd.read_csv("./data/stock_prices/{date}.csv"
                                                  .format(date = start_date), 
                                                  index_col = 'CIK')
                                                  .replace({0: np.nan}))
df_stock_prices_at_prediction_date['stock_price_at_prediction_date'] = pd.to_numeric(df_stock_prices_at_prediction_date['stock_price_at_prediction_date'], errors='coerce')

series_stock_prices_at_end_of_period=(pd.read_csv("./data/stock_prices/{date}.csv"
                                                   .format(date = end_date), index_col='CIK')
                                                   .stock_price_at_prediction_date
                                                   .rename('stock_prices_at_end_of_period')
                                                   .replace({0: np.nan}))
series_stock_prices_at_end_of_period = pd.to_numeric(series_stock_prices_at_end_of_period, errors='coerce')

df_market_cap = pd.read_csv("./data/market_cap/{date}.csv".format(date = start_date), index_col='CIK')
df_market_cap['market_cap_at_prediction_date'] = pd.to_numeric(df_market_cap['market_cap_at_prediction_date'], errors='coerce').astype(float)
print(df_market_cap['market_cap_at_prediction_date'].dtypes)
print(df_market_cap.head())

df_risk_scores = pd.read_csv("./data/risk_scores/{date}.csv".format(date = start_date), index_col='CIK')
df_risk_scores['risk_score'] = pd.to_numeric(df_risk_scores['risk_score'], errors='coerce')

df_portfolio = pd.concat([df_stock_prices_at_prediction_date, 
                          series_stock_prices_at_end_of_period, 
                          df_market_cap, df_risk_scores], axis=1)
df_portfolio = df_portfolio[df_portfolio.index.isin(ciks['CIK'])]
print(df_portfolio.dtypes['market_cap_at_prediction_date'])

# (df_portfolios
# .assign(stock_pct_change = df_portfolio.eval('(stock_prices_at_end_of_period - stock_price_at_prediction_date)/stock_price_at_prediction_date'),
#         # belong_to_index = df_portfolio.index.isin(ciks),
#         )
# .query('belong_to_index & (market_cap > @market_cap_threshold)')
# .assign(weight = lambda df: df.eval('market_cap / market_cap.sum()'))
# .assign(pct_change_contribution = lambda df: df.eval('stock_pct_change * weight'))
# )
df_portfolio['stock_pct_change'] = ((df_portfolio['stock_prices_at_end_of_period'] 
                                    - df_portfolio['stock_price_at_prediction_date']) 
                                    / df_portfolio['stock_price_at_prediction_date'])
df_most_risky_portfolio = df_portfolio.nlargest(top_risk, 'risk_score') 
df_excluding_most_risky = df_portfolio[~df_portfolio.index.isin(df_most_risky_portfolio.index)]


def compute_portfolio_pct_change(df_portfolio: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    """
    Returns
    -------
    pct_change: float
        The pct change of the portfolio
    df_portfolio: pd.DataFrame
        The portfolio with the contribution of each company
    """
    total_market_cap = df_portfolio['market_cap_at_prediction_date'].sum()
    # print(total_market_cap)
    df_portfolio['weight'] = df_portfolio['market_cap_at_prediction_date'] / total_market_cap
    df_portfolio['pct_change_contribution'] = df_portfolio['stock_pct_change'] * df_portfolio['weight']
    total_pct_change = df_portfolio['pct_change_contribution'].sum()
    assert df_portfolio.weight.sum() == 1
    return total_pct_change
compute_portfolio_pct_change(df_most_risky_portfolio)

# def analyze_portfolio(start_date:datetime, end_date:datetime, index_name:str) -> Dict[str, Any]:
#     lst_dates_portfolio_pct_changes = []
#     for date_str in dates_strs:
#         # creating the record information
#         date_portfolios_changes ={
#             'date': date_str,
#             'index_portfolio_pct_change': ,
#             'index_portfolio without riskiest percentile change': -50,
#             'index_riskiest_only_portfolio': 30,
#             }
#         lst_dates_portfolio_pct_changes.append(date_portfolios_changes)