import numpy as np
import pandas as pd
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import Dict, Any, Tuple

""" This script intakes campany data over time
    and calculates the % change in stock price
    relative to it's market value. 
    
    How?
    Combining relavent data: CIK, market cap,
    risk score, and company stock price. Then 
    performing vectorized operations to efficiently
    calculate the weight contribution and stock
    price percent change.
    """

with open('config.json', 'r') as file:
    config = json.load(file)
index = config["index"]
top_risk = config['exclude_top_risk']
duration = config['duration']

def setup(start_date, end_date):
    """
    Returns
    -------
    df_portfolio: all companies in index, 
    df_most_risky_portfolio: top (exclude_top_risk) companies in index with highest risk score, 
    df_excluding_most_risky_portfolio: companies in index not in df_most_risky_portfolio,
    lst_zero_stock_price_at_prediction_date: CIK of companies whos stock price is 0 at prediction date,
    lst_zero_stock_price_at_end_of_period: CIK of companies whos stock price is 0 at end of prediction period
    """
    cik_path = ("./data/indexes/{index}/{date}.csv"
                .format(index = index, date = start_date))
    ciks = pd.read_csv(cik_path)
    lst_zero_stock_price_at_prediction_date = []
    lst_zero_stock_price_at_end_of_period = []

    df_stock_prices_at_prediction_date = (pd.read_csv("./data/stock_prices/{date}.csv"
                                                  .format(date = start_date), 
                                                  index_col = 'CIK'))
    df_stock_prices_at_prediction_date['stock_price_at_prediction_date'] = pd.to_numeric(
        df_stock_prices_at_prediction_date['stock_price_at_prediction_date'], errors='coerce')
    lst_zero_stock_price_at_prediction_date = [df_stock_prices_at_prediction_date['stock_price_at_prediction_date'] == 0].index.tolist()
    df_stock_prices_at_prediction_date = series_stock_prices_at_end_of_period['stock_price_at_prediction_date'].replace({0: np.nan})

    series_stock_prices_at_end_of_period= (pd.read_csv("./data/stock_prices/{date}.csv"
                                                   .format(date = end_date), index_col='CIK')
                                                   .stock_price_at_prediction_date
                                                   .rename('stock_price_at_end_of_period'))
                                                #    .replace({0: np.nan}))
    series_stock_prices_at_end_of_period = (pd.to_numeric(series_stock_prices_at_end_of_period, 
                                                          errors='coerce')
                                                          .replace({0: np.nan}))
    lst_zero_stock_price_at_end_of_period = [series_stock_prices_at_end_of_period == 0].index.tolist()
    series_stock_prices_at_end_of_period = series_stock_prices_at_end_of_period.replace({0: np.nan})

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
    return (df_portfolio, 
            df_most_risky_portfolio, 
            df_excluding_most_risky_portfolio,
            lst_zero_stock_price_at_prediction_date,
            lst_zero_stock_price_at_end_of_period)

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
    assert np.isclose(df__of_portfolio['weight'].sum(), 1.0)
    return total_pct_change

def analyze_portfolio(start_date:datetime, end_date:datetime) -> list[Dict]:
    """
    Returns
    -------
    Dict[str, Any]
    """
    (df_portfolio, 
    df_most_risky_portfolio, 
    df_excluding_most_risky_portfolio,
    lst_zero_stock_price_at_prediction_date,
    lst_zero_stock_price_at_end_of_period) = setup(start_date, end_date)
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

def parse_date(date_str):
    year, month = date_str[1:5], date_str[7:]
    return datetime(int(year), int(month), 1)

def itterate_over_all_dates():
    start = parse_date('y2021_m1')
    end = parse_date('y2023_m10')
    lst_records = []
    while start <= end:
        interval_start_date = "y{year}_m{month}".format(year = start.year, month = start.month)
        interval_end_date = "y{year}_m{month}".format(year = start.year, month = start.month) #add duration relativeDel

        analyze_portfolio()

        start = start + relativedelta(monhs = duration)
        

    (df_portfolio, 
     df_most_risky_portfolio, 
     df_excluding_most_risky_portfolio,
     lst_zero_stock_price_at_prediction_date,
     lst_zero_stock_price_at_end_of_period) = setup("y2021_m1", "y2021_m4")
# check format from email replace date to _ summary
    # save these portfolios to out