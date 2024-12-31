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
        print(len(self.stocks))

    def get_all_symbols_information(self):
        all_news = []
        all_summarys = []
        n=0
        for symbol in self.stocks:
            print(n)
            n+=1
            stock_summary = self.get_summary(symbol)
            if stock_summary.get("marketCap", 0) > 100000000:
                all_summarys.append(stock_summary)
                stock_news = self.get_news(symbol)
                all_news += stock_news
        return all_news, all_summarys

    def get_summary(self, symbol):
        params = {"apiKey": os.getenv("POLYGON_TOKEN")}
        response = requests.get(url=STOCKS_DATA_CONFIG.POLYGON_FUNDAMENTALS_URL + symbol, params=params)
        response_json = response.json()
        long_business_summary = response_json.get("results", {"description": ""}).get('description', "")
        market_cap = round(response_json.get("results", {"market_cap": 0}).get('market_cap', 0))
        renamed_company_summary = {"symbol": symbol, "company_overview": long_business_summary, "marketCap": market_cap}
        print("summary")
        return renamed_company_summary

    def get_news(self, symbol):
        params = {"ticker": symbol,
                  "published_utc.gte": self.start_time,
                  "published_utc.lte": self.end_time,
                  "limit": 3,
                  "apiKey": os.getenv("POLYGON_TOKEN")}
        response = requests.get(url=STOCKS_DATA_CONFIG.POLYGON_NEWS_URL, params = params)
        news = response.json()["results"]
        keys_to_keep = ["title", "article_url"]
        latest_news = [{key: d[key] for key in keys_to_keep if key in d} for d in news]
        key_mapping = {"title": "news_data", "article_url": "news_source"}
        renamed_latest_news = [{key_mapping.get(k, k): v for k, v in news.items()} for news in latest_news]
        renamed_latest_news = [{**data, "symbol": symbol} for data in renamed_latest_news]
        print("news")
        return renamed_latest_news



