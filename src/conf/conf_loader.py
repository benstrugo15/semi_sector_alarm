from pydantic import BaseModel
from typing import List
import yaml
from pathlib import Path


class OpenAiConf(BaseModel):
    URL: str
    RETRY: int
    MODEL: str
    ROLE: str


class StocksDataConf(BaseModel):
    EOD_URL: str
    SYMBOLS_ROUTE: str
    PRICES_ROUTE: str
    NASDAQ: str
    NYSE: str
    RETRY: int
    PERCENT_FILTER: int
    FINNHUB_NEWS_URL: str
    POLYGON_FUNDAMENTALS_URL: str
    POLYGON_NEWS_URL: str


class GmailConf(BaseModel):
    FROM: str
    TO: List[str]
    SMTP_SERVER: str
    SMTP_PORT: int


def load_config(file_name: str):
    file_path = Path(__file__).parent / file_name
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        return data


STOCKS_DATA_CONFIG = StocksDataConf(**load_config("stocks_data_conf.yaml"))
OPEN_AI_CONFIG = OpenAiConf(**load_config("openai_conf.yaml"))
GMAIL_CONFIG = GmailConf(**load_config('gmail.yaml'))