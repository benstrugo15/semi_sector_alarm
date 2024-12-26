import requests
from src.conf.conf_loader import STOCKS_DATA_CONFIG
from datetime import datetime, timedelta
import aiohttp
import asyncio
from aiolimiter import AsyncLimiter
from typing import List, Dict
import pandas as pd
import os

class StocksDataFinder:
    def __init__(self, start_time: str, end_time: str):
        self.start_time = start_time
        self.end_time = end_time
        self.async_limiter = AsyncLimiter(2,1)


    async def get_relevant_data(self):
        all_nasdaq_symbols = self.create_symbols_query(STOCKS_DATA_CONFIG.NASDAQ)[:50]
        all_nyse_symbols = self.create_symbols_query(STOCKS_DATA_CONFIG.NYSE)[:50]
        all_us_symbols = all_nyse_symbols + all_nasdaq_symbols
        all_symbols_data = await self.create_querys_pool(all_us_symbols)
        return all_symbols_data

    @staticmethod
    def create_symbols_query(stock_exchange: str):
        url = STOCKS_DATA_CONFIG.EOD_URL + STOCKS_DATA_CONFIG.SYMBOLS_ROUTE + stock_exchange
        params = {
            'api_token': os.getenv("EOD_TOKEN"),
            'exchange': 'US',
            'fmt': 'json'
        }
        response = requests.get(url=url, params=params)
        symbols = [x["Code"] for x in response.json()]
        return symbols

    async def create_querys_pool(self, symbols: List[str]):
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_stock_data(session, symbol) for symbol in symbols]
            return await asyncio.gather(*tasks)

    async def fetch_stock_data(self, session, symbol):
        url = STOCKS_DATA_CONFIG.EOD_URL + STOCKS_DATA_CONFIG.PRICES_ROUTE + symbol + ".US"
        params = {
            'from': self.start_time,
            'to': self.end_time,
            'period': 'd',
            'api_token': os.getenv("EOD_TOKEN"),
            'fmt': 'json'
            }
        await self.async_limiter.acquire()
        max_retry = STOCKS_DATA_CONFIG.RETRY
        async with session.get(url, params=params) as response:
            print("hey")
            for i in range(max_retry):
                try:
                    response_json = await response.json()
                    response_json = [{**x, "symbol": symbol} for x in response_json]
                    return response_json
                except:
                    if i == max_retry - 1:
                        print(f"HTTP Error {response.status}: {await response.text()}")
                        return []

async def main():
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    finnhub_finder = StocksDataFinder(week_ago, today)
    data = await finnhub_finder.get_relevant_data()
    all_relevant_data = pd.concat([pd.DataFrame(x) for x in data if x != []])
    return all_relevant_data

if __name__ == '__main__':
    a = asyncio.run(main())
    print(a)