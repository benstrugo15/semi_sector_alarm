import requests
from typing import Union, Dict, List, Any
from src.conf.conf_loader import OPEN_AI_CONFIG
import json
import os


class GPTApi:
    def __init__(self, upside_stocks: Dict[str, Any]):
        self.upside_stocks = upside_stocks

    def gpt4_pipline(self):
        relevant_sectors_prompt = self.create_sector_tag_prompt()
        sector_data = relevant_sectors_prompt + json.dumps(self.upside_stocks)
        relevant_sectors = self.query_gpt4(sector_data)
        exploration_prompt = self.create_exploration_prompt()
        sectors_with_exploration = exploration_prompt + json.dumps(relevant_sectors)
        sectors_with_exploration_data = self.query_gpt4(sectors_with_exploration)
        email_prompt = self.create_email_prompt()
        email_pdf = email_prompt + json.dumps(sectors_with_exploration_data)
        email_data = self.query_gpt4(email_pdf)
        return email_data

    def query_gpt4(self, message_text):
        data = {
            "model": OPEN_AI_CONFIG.MODEL,
            "messages": [{"role": OPEN_AI_CONFIG.ROLE, "content": message_text}]
        }
        headers = {"Content-Type": "application/json", "Authorization": os.getenv("OPENAI_TOKEN")}
        response = requests.post(OPEN_AI_CONFIG.URL, headers=headers, json=data)
        return response.json()

    @staticmethod
    def create_sector_tag_prompt():
        return "can you categorize the following list of stocks into their specific micro-sectors" \
               "or sub-industries? return it to me in this format: list of dicts, every dict will have 2 keys" \
               "micro_sector: str, stocks: Lisr[str]," \
               " and then filter only the micro_sector with 2 or more values" \

    @staticmethod
    def create_exploration_prompt():
        return "for every semi_sector i want you to check multiple things:" \
               "1. give a short summary of the semi_sector, " \
               "give a summary on every stock in the semi_sector" \
               "2. tell me for every semi_sector if this future oriented semi_sector"\
               "3. check news in the internet from the last week on every semi_sector and every stock in the semi secotr" \
               "4. for every semi sector i want you to give me a very short summary of why the sector is up this week,"\
               "do it the same for every stock"\
               "check only in american sources"\
                "translate everything to hebrew and give all sources url"

    @staticmethod
    def create_email_prompt():
        return """transform data to beautiful email:
                i want you to take all the data and create beautiful email, bold titles and paragraph names.
                first, will be with title 'סמי סקטורים עתידניים בפריצה'
                in the start, will be the current date and the name of all the relevant semi sectors.
                after, for every semi sectors, i want you to prepare the data like this:
                first paragraph: "סקירה קצרה על הסקטור"
                second paragraph: "סקירה קצרה על הסקטור"
                third paragraph: "למה הסקטור הוא עם פוטנציאל לעתיד"
                forth paragraph: "החדשות שהיו השבוע על הסקטור"
                i want every paragraph will be on every semi_sector and if there is no data
                in specific paragraph, please write 'ללא נתונים'"""