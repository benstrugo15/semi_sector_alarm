import asyncio
from datetime import datetime, timedelta
from src.alarm_pipeline.alarm_pipeline import AlarmPipe


async def main():
    for i in range(5):
        alarm_pipe = AlarmPipe(datetime.now())
        try:
            repetitive_upside_stocks = await alarm_pipe.get_repetitive_upside_stocks()
            all_symbols_summary, all_symbols_news = alarm_pipe.get_stocks_informations(repetitive_upside_stocks)
            explore_stocks = alarm_pipe.stock_exploration(all_symbols_summary, all_symbols_news,
                                                          repetitive_upside_stocks)
            alarm_pipe.send_email(explore_stocks)
            break
        except ValueError as e:
            if i == 4:
                alarm_pipe.send_email(str(e), True)


if __name__ == '__main__':
    asyncio.run(main())
