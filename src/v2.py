import json
import pandas as pd
from datetime import datetime

with open('config.json', 'r') as file:
    config = json.load(file)
index = config["index"]
top_risk = config['exclude_top_risk']
duration = config['duration']
start_date = config['start_date']
end_date = config['end_date']
cik_path = "./data/indexes/{index}/{date}.csv" 
cik_path = cik_path.format(index = index, date = start_date)
ciks = pd.read_csv(cik_path)
lst_zero_stock_price = []

path_risk_scores = "./data/risk_scores/{date}.csv".format(date = start_date)
risk_df = pd.read_csv(path_risk_scores)
risk_df_sorted = risk_df.sort_values(by='risk_score', ascending=False)
top_risk_companies = risk_df_sorted.head(top_risk)['CIK']
print(top_risk_companies)

def stock_price_change_percent(first, second):
    if first == 0 or second == 0:
        return 0
    return (second-first)/first

def weight(company_market_cap, total_market_cap):
    return company_market_cap/total_market_cap

def porftolio_price_change_contribution(weight, stock_price_change_percent):
    return weight*stock_price_change_percent

def parse_date(date_str):
    year, month = date_str[1:5], date_str[7:]
    return datetime(int(year), int(month), 1)
# from dateutil.relativedelta import relativedelta

# def generate_all_paths(start_date, end_date, base_path):
#     start = parse_date(start_date)
#     end = parse_date(end_date)
#     file_paths = []
#     while start <= end:
#         formatted_date = "y{year}_m{month}".format(year = start.year, month = start.month)
#         file_path = "{base_path}/{formatted_date}.csv".format(base_path = base_path, formatted_date = formatted_date)
#         file_paths.append(file_path)
#         if start.month == 12:
#             start = start.replace(year=start.year + 1, month=1)
#         else:
#             start = start.replace(month=start.month + 3)
#     return file_paths

def calculate_stock_price_change_percent(cik, start_date, end_date):
    path_start_stock_price = "./data/stock_prices/{date}.csv".format(date = start_date)
    path_end_stock_price = "./data/stock_prices/{date}.csv".format(date = end_date)
    df_start_stock_price = pd.read_csv(path_start_stock_price)
    df_end_stock_price = pd.read_csv(path_end_stock_price)

    row_start = df_start_stock_price[df_start_stock_price['CIK'] == cik]
    row_end = df_end_stock_price[df_end_stock_price['CIK'] == cik]
    price_start = row_start.iloc[0]['stock_price_at_prediction_date']
    price_end = row_end.iloc[0]['stock_price_at_prediction_date']
    print(price_start)

    # if not bool(price_start) ^ bool(price_end):
    #     raise ValueError("unusable stock price")

    return stock_price_change_percent(int(price_start), int(price_end))
    
def calculate_weight(cik, date):
    path_market_cap = "./data/market_cap/{date}.csv".format(date = date)
    df_market_cap = pd.read_csv(path_market_cap)

    total_market_cap = df_market_cap['market_cap_at_prediction_date'].sum()
    company_market_cap = df_market_cap[df_market_cap['CIK']==cik].iloc[0]['market_cap_at_prediction_date']

    return weight(company_market_cap, total_market_cap)

def entire_portfolio():
    total_market_cap = 0
    price_change_contribution = 0

    for cik in ciks['CIK']:
        price_change_percent = calculate_stock_price_change_percent(cik, start_date, end_date)
        if price_change_percent == 0:
            lst_zero_stock_price.append(cik)
            continue
        company_weight = calculate_weight(cik, start_date)
        total_price_change_contribution += porftolio_price_change_contribution(company_weight, price_change_percent)
    
    return total_price_change_contribution

def index_portfolio_excluding_riskiest():
    total_market_cap = 0
    price_change_contribution = 0

    for cik in ciks['CIK']:
        if cik not in top_risk_companies.values:
            price_change_percent = calculate_stock_price_change_percent(cik, start_date, end_date)
            company_weight = calculate_weight(cik, start_date)
            total_price_change_contribution += porftolio_price_change_contribution(company_weight, price_change_percent)
    
    return total_price_change_contribution

def index_portfolio_riskiest_only():
    total_market_cap = 0
    price_change_contribution = 0

    for cik in top_risk_companies['CIK']:
        price_change_percent = calculate_stock_price_change_percent(cik, start_date, end_date)
        company_weight = calculate_weight(cik, start_date)
        total_price_change_contribution += porftolio_price_change_contribution(company_weight, price_change_percent)
    
    return total_price_change_contribution

def generate_summary():
    portfolio_data = []
    portfolio_data.append([entire_portfolio(), index_portfolio_excluding_riskiest(), index_portfolio_riskiest_only()])
    df_summary = pd.DataFrame(portfolio_data, columns=['Entire Portfolio', 'Excluding Riskiest Portfolio', 'Riskiest Only Portfolio'])
    df_summary.to_csv("/out/{index}/{duration}/index_portfolio/{start_date}".format(index=index, duration=duration, start_date=start_date), index=False)

print(lst_zero_stock_price)
generate_summary()