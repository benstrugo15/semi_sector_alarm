import asyncio

from src.alarm_pipeline.alarm_pipeline import AlarmPipe
from datetime import datetime

async def main():
    date_now = datetime.now()
    alarm_pipe = AlarmPipe(date_now)
    repetative_upside_stocks = await alarm_pipe.get_repetative_upside_stocks()
    # repetative_upside_stocks = ["smr", "cvx"]
    # repetative_upside_stocks = ["smr", "nee", "xom", "cvx", "lng", "oklo", "eqt", "btu","sedg", "vlo", "arch"]
    all_symbols_summary, all_symbols_news = alarm_pipe.get_stocks_informations(repetative_upside_stocks)
    explore_stocks = alarm_pipe.stock_exploration(all_symbols_summary, all_symbols_news, repetative_upside_stocks)
    send_mail = alarm_pipe.send_email(explore_stocks)
    print(send_mail)

if __name__ == '__main__':
    asyncio.run(main())