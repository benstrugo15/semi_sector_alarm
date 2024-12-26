import requests
from finnhub import FinnhubBase
import json
from datetime import datetime


class TodayData(FinnhubBase):
    def __init__(self, start_time: datetime, end_time: datetime):
        super().__init__(start_time, end_time)

    def create_query(self):
        pass

    def parse_data(self):
        pass


