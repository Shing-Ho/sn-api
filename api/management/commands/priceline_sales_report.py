import requests

from typing import Dict
from datetime import datetime

from django.core.management import BaseCommand

from api import logger

from api.hotel.adapters.priceline.priceline_sales_report import PricelineSalesReport

MAIL_GUN_URL = "https://api.mailgun.net/v3/sandbox4d76d5beb24f4ba790d3ccf7cda332c4.mailgun.org/messages"
MAIL_GUN_API_KEY = "4fc764e45639a2008a075f69a0706591-2fbe671d-1bc16189"
MAIL_GUN_FROM = "Mailgun Sandbox <postmaster@sandbox4d76d5beb24f4ba790d3ccf7cda332c4.mailgun.org>"
MAIL_GAN_TO = "rob@simplenight.com"

class UnmatchedSaleItem:
    def __init__(self, sale_item: Dict):
        self.sale_item = sale_item

    def __repr__(self):
        record_locator = self.sale_item['sales_id']
        hotel_name = self.sale_item['hotel_name']
        booking_date = self.sale_item['reservation_date_time']

        return f"""
            Record Locator: {record_locator}
            Hotel Name: {hotel_name}
            Booking Date: {booking_date}"""

class Command(BaseCommand):
    def handle(self, *args, **options):
        priceline_sales_report = PricelineSalesReport()
        sales_data = priceline_sales_report.find_unmatched_bookings()

        unmatched_sales_items = [UnmatchedSaleItem(x) for x in sales_data]

        email_body = ""
        for item in unmatched_sales_items:
            email_body += str(item) + "\n"

        if email_body != "":
            response = self.send_email(email_body)
            logger.info(response.json())
        else:
            logger.warn("No differences")

    def send_email(self, text):
        today = datetime.now().date()

        subject = "PCLN Ghost Report " + str(today)

        return requests.post(
            MAIL_GUN_URL,
            auth=("api", MAIL_GUN_API_KEY),
            data={
                "from": MAIL_GUN_FROM,
                "to": MAIL_GAN_TO,
                "subject": subject,
                "text": "CSV file has been attached."
            }
        )