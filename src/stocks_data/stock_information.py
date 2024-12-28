import requests
from datetime import datetime, timedelta
from typing import List
import os
from src.conf.conf_loader import STOCKS_DATA_CONFIG
import yfinance as yf
import pandas as pd


class StockInformation:
    def __init__(self, stocks: pd.DataFrame, start_time: str, end_time: str):
        self.stocks = list(set(stocks['symbol'].to_list()))
        self.start_time = start_time
        self.end_time = end_time

    def get_all_symbols_information(self):
        all_news = []
        all_summarys = []
        for symbol in self.stocks:
            stock_news = self.get_news(symbol)
            stock_summary = self.get_summary(symbol)
            all_news += stock_news
            all_summarys.append(stock_summary)
        return all_news, all_summarys

    def get_summary(self, symbol):
        stock = yf.Ticker(symbol)
        company_info = stock.info
        keys_to_keep = ['longBusinessSummary', 'symbol']
        company_summary = {key: value for key, value in company_info.items() if key in keys_to_keep}
        key_mapping = {"longBusinessSummary": "company_overview"}
        renamed_company_summary = {key_mapping.get(k, k): v for k, v in company_summary.items()}
        return renamed_company_summary

    def get_news(self, symbol):
        params = {"symbol": symbol,
                  "from": self.start_time,
                  "to": self.end_time,
                  "token": os.getenv("FINNHUB_TOKEN")}
        response = requests.get(url=STOCKS_DATA_CONFIG.FINNHUB_URL, params = params)
        news = response.json()[:3]
        keys_to_keep = ["headline", "url", "related"]
        latest_news = [{key: d[key] for key in keys_to_keep if key in d} for d in news]
        key_mapping = {"headline": "news_data", "url": "news_source", "related": "symbol"}
        renamed_latest_news = [{key_mapping.get(k, k): v for k, v in news.items()} for news in latest_news]
        return renamed_latest_news



