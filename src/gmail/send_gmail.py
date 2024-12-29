import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.conf.conf_loader import GMAIL_CONFIG
from datetime import datetime
import os
from typing import Dict, List


class EmailSender:
    def __init__(self, gmail_data: List[Dict[str, str]]):
        self.gmail_data = gmail_data
        self.unique_sub_sectors = list(set(list({entry['sub_sector'] for entry in gmail_data})))
        self.date = datetime.now().strftime("%Y-%m-%d")

    def send_email(self):
        msg = MIMEMultipart()
        msg['From'] = GMAIL_CONFIG.FROM
        msg['To'] = ', '.join(GMAIL_CONFIG.TO)
        msg['Subject'] = " מיקרו סקטורים בפריצה " + self.date
        body = self.build_html()
        msg.attach(MIMEText(body, 'html'))
        try:
            with smtplib.SMTP(GMAIL_CONFIG.SMTP_SERVER, GMAIL_CONFIG.SMTP_PORT) as server:
                server.starttls()
                password = os.getenv("GMAIL_PASSWORD")
                server.login(GMAIL_CONFIG.FROM, password)
                text = msg.as_string()
                server.sendmail(GMAIL_CONFIG.FROM, GMAIL_CONFIG.TO, text)
                print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def build_html(self):
        start_html = self.build_start_html()
        middle_html = self.build_middle_html(start_html)
        end_html = self.build_end_html(middle_html)
        return end_html

    def build_start_html(self):
        html_content = f"""
        <html>
        <head>
            <title>סמי סקטורים עתידניים בפריצה</title>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h1 {{ color: navy; }}
                h2, h3 {{ color: darkred; }}
                p {{ margin-left: 20px; }}
                a {{ text-decoration: none; color: blue; }}
                .large {{ font-size: large; font-weight: bold; }}
                .medium {{ font-size: medium; }}
            </style>
        </head>
        <body>
            <h1>סמי סקטורים עתידניים בפריצה</h1>
            <p class="large">תאריך: {self.date}</p>
            <div class="medium">סקטורים:</div>
            <ul>
        """
        for sub_sector in self.unique_sub_sectors:
            html_content += f"<li>{sub_sector}</li>"
        html_content += "</ul>"
        return html_content

    def build_middle_html(self, html_content):
        for sub_sector in self.unique_sub_sectors:
            html_content += f"<h2>{sub_sector}</h2>"
            sector_data = [item for item in self.gmail_data if item['sub_sector'] == sub_sector]
            for item in sector_data:
                news_pieces = list(set(item['news_data'].split('***')))
                sources = list(set(item['news_source'].split('***')))
                news_html = "<ul>" + "".join(
                    f"<li>{news.strip()} (<a href='{src.strip()}'>מקור</a>)</li>" for news, src in
                    zip(news_pieces, sources)) + "</ul>"

                html_content += f"""
                <h3>{item['symbol']}</h3>
                <p><strong>שינוי יומי:</strong> {format(item['marketCap'])} + "$"%</p>
                <p><strong>מחיר:</strong> {item['last_price']}</p>
                <p><strong>שינוי יומי:</strong> {str(round(int(item['last_percent'],2)))}%</p>
                <p><strong>שינוי ב7 ימי המסחר האחרונים:</strong> {str(round(int(item['start_end_percent'],2)))}%</p>
                <p><strong>סקירה על הסאב סקטור:</strong> {item['sub_sector_overview']}</p>
                <p><strong>סקירה על המניות:</strong> {item['company_overview']}</p>
                <p><strong>האם הסקטור הוא עם פוטנציאל לעתיד:</strong> {'כן' if item['is_semi_sector_future_potential'] else 'לא'} - {item['semi_sector_future_potential_overview']}</p>
                <p><strong>חדשות תומכות:</strong> {news_html}</p>
                """
        return html_content

    def build_end_html(self, html_content):
        html_content += """
        </body>
        </html>
        """
        return html_content

if __name__ == '__main__':
    data = [
    {
        'symbol': 'ABG',
        'sub_sector': 'Automotive Retail',
        'sub_sector_overview': 'This sub-sector encompasses companies involved in the selling of both new and used vehicles, including parts, vehicle repair, and maintenance services.',
        'is_semi_sector_future_potential': False,
        'semi_sector_future_potential_overview': 'Despite the constant demand for vehicles, this sector does not expect extraordinary breakthroughs, but continues to evolve with market trends and technologies.',
        'news_data': 'Asbury Automotive Group, Inc. (NYSE:ABG), might not be a large cap stock, but it saw a decent share price growth...',
        'news_source': 'https://finnhub.io/api/news?id=8f8e8bf59482da640d39861ca2a733e3132d922f558c199a88da6f19f5ea92b2',
        'company_overview': 'Asbury Automotive Group, Inc., together with its subsidiaries, operates as an automotive retailer in the United States. It offers a range of automotive products and services, including new and used vehicles; vehicle repair and maintenance services, replacement parts, and collision repair services.',
        'last_price': 249.27,
        'last_percent': 2.23,
        'start_end_percent': 5.41
    },
    {
        'symbol': 'AAOI',
        'sub_sector': 'Fiber-Optic Networking',
        'sub_sector_overview': 'This segment covers companies that design, manufacture, and sell fiber-optic networking products serving telecom equipment manufacturers, data center operators, and internet service providers.',
        'is_semi_sector_future_potential': True,
        'semi_sector_future_potential_overview': 'With the increasing demand for high-speed internet and the expansion of data centers, there are expectations for significant advancements in optic technology.',
        'news_data': 'Applied Optoelectronics (AAOI) just unveiled an update. Applied Optoelectronics announced the closure of an exchange agreement, swapping $76.7 million in 2026 Notes for $125 million in 2030 Notes, 1.487 million shares of common stock, and a cash amount covering accrued interest.',
        'news_source': 'https://finnhub.io/api/news?id=6c155daf83a7068f83059edb3959c38cb9e3aec5fd605dc3fa8e61e138c03e83',
        'company_overview': 'Applied Optoelectronics, Inc. designs, manufactures, and sells fiber-optic networking products in the United States, Taiwan, and China. It offers optical modules, optical filters, lasers, laser components, subassemblies, transmitters, and transceivers, turn-key equipment, headend, node, distribution equipment, and amplifiers.',
        'last_price': 40.94,
        'last_percent': 1.12,
        'start_end_percent': 8.55
    }
]
    a = EmailSender(data)
    b = a.send_email()
    print(b)