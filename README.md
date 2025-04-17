# 📊 Semi Sector Alerm

A smart, automated stock scanner that combines quantitative analysis, NLP, and AI to surface high-potential investment opportunities — straight to your inbox, every day.

---

## 🔍 Overview

Stock Scanner AI is a Python-based project designed to automatically scan the stock market for investment-worthy assets using both technical and fundamental analysis.  
It integrates financial data APIs, custom screening logic, and large language models to generate clear insights and daily trade ideas.

---

## 🧠 Key Features

- 🗓 **Daily Automated Scans** – runs every morning to evaluate market trends
- 📈 **Quantitative Filters** – filters based on volume spikes, unusual options activity, relative strength, volatility, etc.
- 📊 **Fundamental Signals** – screens based on earnings growth, valuations, insider activity, and more
- 🧠 **AI-Powered Insights** – uses LLMs to analyze financial news and generate summaries for selected tickers
- 📬 **Email Reports** – delivers a curated daily summary of top opportunities, including rationale and technical/fundamental context
- ⚙️ **Fully Configurable** – adjust thresholds, strategies, and risk parameters easily
- 🔌 **Modular Architecture** – supports multiple APIs and data providers like Polygon, Yahoo Finance, and more

---

## 📁 Tech Stack

- **Language:** Python 3.10+
- **Frameworks:** FastAPI, Pandas
- **Scheduling:** APScheduler / cron
- **APIs:** Polygon.io, Yahoo Finance, OpenAI GPT-4
- **Deployment:** Docker-ready, can run on any cloud VM or local machine
- **Output:** HTML email with charts + insights

---

## 🔧 Setup & Usage

1. **Clone the repo**
   ```bash
   git clone https://github.com/benstrugo15/semi_sector_alarm.git
   cd semi_sector_alarm
