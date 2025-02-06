from src.stocks_data.price_analysis import SymbolFinder
from src.gmail.send_gmail import EmailSender
from src.openai_api.GPT import GPTApi
from src.stocks_data.stock_information import StockInformation
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Union


class AlarmPipe:
    def __init__(self, date: datetime):
        self.end_time = date.strftime("%Y-%m-%d")
        self.start_time = (date - timedelta(days=10)).strftime("%Y-%m-%d")

    async def get_repetitive_upside_stocks(self):
        stock_data_finder = SymbolFinder(self.start_time, self.end_time)
        relevant_stocks_prices = await stock_data_finder.get_relevant_data()
        return relevant_stocks_prices

    def get_stocks_informations(self, relevant_symbols: pd.DataFrame):
        stock_information = StockInformation(relevant_symbols, self.start_time, self.end_time)
        all_symbols_news, all_symbols_summary = stock_information.get_all_symbols_information()
        return all_symbols_summary, all_symbols_news

    @staticmethod
    def stock_exploration(all_symbols_summary: List[Dict[str, str]], all_symbols_news, relevant_stocks_prices):
        gpt_api = GPTApi(all_symbols_summary, all_symbols_news, relevant_stocks_prices)
        email_data = gpt_api.gpt4_pipline()
        return email_data

    def send_email(self, email_data: Union[str, List[Dict[str, str]]], is_error=None):
        email_sender = EmailSender(self.end_time)
        send_mail = email_sender.send_email(email_data, is_error)
        return send_mail


