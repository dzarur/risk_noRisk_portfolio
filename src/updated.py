import json
import pandas as pd
from glob import glob
from datetime import datetime

with open('config.json', 'r') as file:
    config = json.load(file)
index = config["index"]
top_risk = config['exclude_top_risk']
duration = config['duration']
start_date = config['start_date']
cik_path = "./data/indexes/{index}/{date}.csv" 
cik_path = cik_path.format(index = index, date = start_date)
ciks = pd.read_csv(cik_path)

def stock_price_change_percent(first, second):
    return (second-first)/first

def weight(company_market_cap, portfolio_total_market_cap):
    return company_market_cap/portfolio_total_market_cap

def porftolio_price_change_contribution(weight, stock_price_change_percent):
    return weight*stock_price_change_percent

def parse_date(date_str):
    year, month = date_str[1:5], date_str[7:]
    return datetime(int(year), int(month), 1)

def generate_all_paths(start_date, end_date, base_path):
    start = parse_date(start_date)
    end = parse_date(end_date)
    file_paths = []
    while start <= end:
        formatted_date = "y{year}_m{month}".format(year = start.year, month = start.month)
        file_path = "{base_path}/{formatted_date}.csv".format(base_path = base_path, formatted_date = formatted_date)
        file_paths.append(file_path)
        if start.month == 12:
            start = start.replace(year=start.year + 1, month=1)
        else:
            start = start.replace(month=start.month + 3)
    return file_paths

def calculate_stock_price_change(cik, start, end):
    pass