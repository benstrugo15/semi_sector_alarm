import pandas as pd
import requests
from typing import Union, Dict, List, Any
from src.conf.conf_loader import OPEN_AI_CONFIG
import json
import os


class GPTApi:
    def __init__(self, stocks_overview: List[Dict[str, str]], stocks_news, relevant_stocks_prices):
        self.stocks_overview = stocks_overview
        self.stocks_news = stocks_news
        self.relevant_stocks_prices = relevant_stocks_prices

    def gpt4_pipline(self):
        relevant_symbols_query = self.create_exploration_prompt(str(self.stocks_overview))
        stocks_semi_sectors = self.query_gpt4(relevant_symbols_query, "exploration_prompt")
        all_relevant_stocks_data = self.merge_stocks_data(stocks_semi_sectors)
        return all_relevant_stocks_data

    def query_gpt4(self, message_text, query_type: str):
        data = {
            "model": OPEN_AI_CONFIG.MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant that provides stock-related insights."
                }

                ,
                {"role": "user",
                  "content": message_text
                  }
            ]
            
        }
        headers = {"Content-Type": "application/json", "Authorization": os.getenv("OPENAI_TOKEN")}
        response = requests.post(OPEN_AI_CONFIG.URL, headers=headers, json=data)
        response_data = response.json()['choices'][0]['message']['content']
        if query_type == "exploration_prompt":
            start_index = response_data.find("[")
            end_index = response_data.rfind("]") + 1
            parse_data = json.loads(response_data[start_index: end_index])
            return parse_data
        return response_data

    def merge_stocks_data(self, stocks_semi_sectors: List[Dict[str, str]]):
        organized_stocks_semi_sectors = pd.DataFrame(stocks_semi_sectors).drop(columns=["company_overview"])
        organized_stocks_semi_sectors = organized_stocks_semi_sectors[organized_stocks_semi_sectors["is_semi_sector_future_potential"] == True]
        organized_stocks_semi_sectors = organized_stocks_semi_sectors.groupby('sub_sector').filter(lambda x: x['symbol'].nunique() >= 2)
        organized_stocks_news = pd.DataFrame(self.stocks_news)
        organized_stocks_overview = pd.DataFrame(self.stocks_overview)
        all_relevant_data = organized_stocks_semi_sectors.\
            merge(organized_stocks_news).\
            merge(organized_stocks_overview).merge(self.relevant_stocks_prices).drop_duplicates()
        grouped = all_relevant_data.groupby('symbol').agg({
            'news_source': '***'.join,'news_data': '***'.join}).reset_index()
        other_columns = all_relevant_data.drop(['news_source', 'news_data'], axis=1).drop_duplicates()
        concat_data = pd.merge(grouped, other_columns, on='symbol', how='left')
        return concat_data.to_dict(orient="records")


    @staticmethod
    def create_sector_tag_prompt():
        return "can you categorize the following list of stocks into their specific micro-sectors" \
               "or sub-industries? return it to me in the same format i sent you, just append for every dict the key semi_sector" \
               "and the value" \
               "and then filter only the micro_sector with 2 or more unique stocks symbols" \

    @staticmethod
    def create_exploration_prompt(symbols: str):
        return f"""
                Provide the response in JSON format, with no ' character,
                i give you list of dicts, every dict have 2 keys: symbol, company_overview,
                the symbol is a stock symbol,
                and the company_overview is a company overview
                use the data i provide you, to add every dict, 4 more keys:
                "sub_sector" and the value of the sub_sector.
                the sub_sector value will be "specific, concise tag of the company",
                "sub_sector_overview" and the value of that - a sub sector brief summary (not company, the sub_sector)
                "is_semi_sector_future_potential" and the value will be true if the semi_sector have
                 extraordinary breakthroughs to change the future, false if it is not,
                "semi_sector_future_potential_overview": the value will be the reason it have 
                extraordinary breakthroughs in the future. 
                if there are stocks symbols that have similar concise, give them the same tag
                understand from the company overview
                the data you need to work on: 
                
                {symbols}"""

    @staticmethod
    def create_email_prompt(stoks_data):
        return f"""transform data to beautiful css, html email:
                all the data i will give you will be translate to hebrew,the email will be full hebrew.
                i want you to take all the data and create beautiful email, bold titles and paragraph names.
                first, will be with title 'סמי סקטורים עתידניים בפריצה':
                in the start,
                will be the current date and the name of all the unique values of sub_sectors.
                under, will be in small title every sub_sector, and row below for every unique 
                symbol in the sub_sector show:
                first "מחיר" will be the value of last_price
                second "שינוי יומי" will be the value of last_percent
                third "שינוי ב7 ימי המסחר האחרוני" will be the value of start_end_percent
                after, for every sub_sectors, i want you to prepare the data like this:
                the sub title will be: sub_sector
                first paragraph: "סקירה על הסאב סקטור" :
                 value will be the value of sub_sector_overview
                second paragraph: "סקירה על המניות" :
                 every sub title will be the value of symbol from the semi sector
                ,and the details will be values of company_overview from the symbol
                third paragraph: "האם הסקטור הוא עם פוטנציאל לעתיד":
                 value will be the value is_semi_sector_futue_potential
                and the details will be the value of semi_sector_futue_potential_overview
                forth paragraph: "חדשות תומכות":
                every sub title will be the value of symbol from the semi sector
                ,and the details will be values of news_data from the symbol,
                and the news_source value of the news_data
                
                i want every paragraph will be on every semi_sector and if there is no data
                in specific paragraph, please write 'ללא נתונים'
                all the links will transform to hyperlink "source"
                
                the data you base on:
                
                {stoks_data}"""