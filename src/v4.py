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
lst_zero_stock_price_at_prediction_date = []
lst_zero_stock_price_at_end_of_period = []

df_stock_prices_at_prediction_date = (pd.read_csv("./data/stock_prices/{date}.csv"
                                                  .format(date = start_date), 
                                                  index_col = 'CIK'))
                                                #   .replace({0: np.nan}))
df_stock_prices_at_prediction_date['stock_price_at_prediction_date'] = pd.to_numeric(
    df_stock_prices_at_prediction_date['stock_price_at_prediction_date'], errors='coerce')
df_stock_prices_at_prediction_date['stock_price_at_prediction_date'] = df_stock_prices_at_prediction_date['stock_price_at_prediction_date'].replace({0: np.nan})

series_stock_prices_at_end_of_period=(pd.read_csv("./data/stock_prices/{date}.csv"
                                                   .format(date = end_date), index_col='CIK')
                                                   .stock_price_at_prediction_date
                                                   .rename('stock_price_at_end_of_period'))
                                                #    .replace({0: np.nan}))
series_stock_prices_at_end_of_period = pd.to_numeric(series_stock_prices_at_end_of_period, errors='coerce')

series_market_cap = (pd.read_csv("./data/market_cap/{date}.csv"
                            .format(date = start_date), 
                            index_col='CIK')
                            .market_cap_at_prediction_date)

series_risk_scores = (pd.read_csv("./data/risk_scores/{date}.csv"
                                 .format(date = start_date), 
                                 index_col='CIK')
                                 .risk_score)

df_portfolio = pd.concat([df_stock_prices_at_prediction_date, 
                          series_stock_prices_at_end_of_period, 
                          series_market_cap, series_risk_scores], axis=1)
df_portfolio = df_portfolio[df_portfolio.index.isin(ciks['CIK'])]
lst_zero_stock_price_at_prediction_date = df_portfolio[df_portfolio['stock_price_at_prediction_date'] == 0].index.tolist()
lst_zero_stock_price_at_end_of_period = df_portfolio[df_portfolio['stock_price_at_end_of_period'] == 0].index.tolist()
df_portfolio['stock_pct_change'] = ((df_portfolio['stock_price_at_end_of_period'] 
                                    - df_portfolio['stock_price_at_prediction_date']) 
                                    / df_portfolio['stock_price_at_prediction_date'])
df_most_risky_portfolio = df_portfolio.nlargest(top_risk, 'risk_score') 
df_excluding_most_risky_portfolio = df_portfolio[~df_portfolio.index.isin(df_most_risky_portfolio.index)]

def compute_portfolio_pct_change(df__of_portfolio: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    """
    Returns
    -------
    pct_change: float
        The pct change of the portfolio
    df_portfolio: pd.DataFrame
        The portfolio with the contribution of each company
    """
    df__of_portfolio = df__of_portfolio.copy()
    total_market_cap = df__of_portfolio['market_cap_at_prediction_date'].sum()
    df__of_portfolio.loc[:, 'weight'] = df__of_portfolio['market_cap_at_prediction_date'] / total_market_cap
    df__of_portfolio.loc[:, 'pct_change_contribution'] = (df__of_portfolio['stock_pct_change'] 
                                               * df__of_portfolio['weight'])
    total_pct_change = df__of_portfolio['pct_change_contribution'].sum()
    # assert df__of_portfolio.weight.sum() == 1 # floating point has rounding errors
    assert np.isclose(df__of_portfolio['weight'].sum(), 1.0)
    return total_pct_change

# def date_to_number(date_str):
#     year, month = date_str[1:5], date_str[7:]
#     return datetime(int(year), int(month), 1) 

# def number_to_string(year: datetime, month: datetime):
#     formatted_date = "y{year}_m{month}".format(year = year, month = month)

# def analyze_portfolio(start_date:datetime, end_date:datetime, index_name:str) -> Dict[str, Any]:
def analyze_portfolio():
    """
    Returns
    -------
    Dict[str, Any]
    """
    # lst_dates_portfolio_pct_changes = []
    # for date_str in dates_strs:
        # creating the record information
    index_portfolio_pct_change = compute_portfolio_pct_change(df_portfolio)
    index_portfolio_excluding_most_risky_pct_change = (
        compute_portfolio_pct_change(df_excluding_most_risky_portfolio))
    index_riskiest_only_portfolio_pct_change =(
        compute_portfolio_pct_change(df_most_risky_portfolio))
    
    record ={
        'perdiod': start_date + "-" + end_date,
        'index_portfolio_pct_change' : index_portfolio_pct_change,
        'index_portfolio_excluding_most_risky_pct_change': index_portfolio_excluding_most_risky_pct_change,
        'index_riskiest_only_portfolio_pct_change': index_riskiest_only_portfolio_pct_change,
        'lst_cik_zero_stock_price_at_prediction_date': lst_zero_stock_price_at_prediction_date,
        'lst_cik_zero_stock_price_at_end_of_period': lst_zero_stock_price_at_end_of_period
        }
    return record

print(analyze_portfolio())