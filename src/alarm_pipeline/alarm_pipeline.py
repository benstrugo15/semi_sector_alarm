from src.stocks_data.price_analysis import SymbolFinder
from src.gmail.send_gmail import EmailSender
from src.openai_api.GPT import GPTApi
from src.stocks_data.stock_information import StockInformation
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict

class AlarmPipe:
    def __init__(self, date_now: datetime):
        self.end_time = (date_now- timedelta(days=3)).strftime("%Y-%m-%d")
        self.start_time = (date_now - timedelta(days=11)).strftime("%Y-%m-%d")

    async def get_repetative_upside_stocks(self):
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

    @staticmethod
    def send_email(email_data: str):
        email_sender = EmailSender(email_data)
        send_mail = email_sender.send_email()
        return send_mail


