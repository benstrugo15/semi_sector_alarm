import asyncio
from datetime import datetime, timedelta
from src.alarm_pipeline.alarm_pipeline import AlarmPipe


async def main():
    while True:
        now = datetime.now()
        next_run = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now >= next_run:
            next_run += timedelta(days=1)
        sleep_duration = (next_run - now).total_seconds()
        await asyncio.sleep(sleep_duration)
        if next_run.weekday() not in [0, 6]:
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
                    alarm_pipe.send_email(str(e), True)


if __name__ == '__main__':
    asyncio.run(main())
