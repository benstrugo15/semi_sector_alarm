import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.conf.conf_loader import GMAIL_CONFIG
from datetime import datetime
import os


class EmailSender:
    def __init__(self, gmail_data: str):
        self.gmail_data = gmail_data
        self.date = datetime.now().strftime("%Y-%m-%d")

    def send_email(self):
        msg = MIMEMultipart()
        msg['From'] = GMAIL_CONFIG.FROM
        msg['To'] = ', '.join(GMAIL_CONFIG.TO)
        msg['Subject'] = " מיקרו סקטורים בפריצה " + self.date
        body = self.gmail_data
        msg.attach(MIMEText(body, 'plain'))
        try:
            with smtplib.SMTP(GMAIL_CONFIG.SMTP_SERVER, GMAIL_CONFIG.SMTP_PORT) as server:
                server.starttls()
                server.login(GMAIL_CONFIG.FROM, os.getenv("GMAIL_PASSWORD"))
                text = msg.as_string()
                server.sendmail(GMAIL_CONFIG.FROM, GMAIL_CONFIG.TO, text)
                print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")
