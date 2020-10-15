import json
import requests


from typing import Dict
from datetime import datetime, timedelta

from django.core.management import BaseCommand

from api.models.models import HotelBooking

ENDPOINT = "https://api-sandbox.rezserver.com/api/shared/getTRK.Sales.Select.Hotel?format=json&"
REF_ID = "10046"
API_KEY = "990b98b0a0efaa7acf461ff6a60cf726"

MAIL_GUN_URL = "https://api.mailgun.net/v3/sandbox4d76d5beb24f4ba790d3ccf7cda332c4.mailgun.org/messages"
MAIL_GUN_API_KEY = "4fc764e45639a2008a075f69a0706591-2fbe671d-1bc16189"
MAIL_GUN_FROM = "Mailgun Sandbox <postmaster@sandbox4d76d5beb24f4ba790d3ccf7cda332c4.mailgun.org>"

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
        sales_data = self.get_sales_report()
        priceline_sales_ids = [x["sales_id"] for x in sales_data]

        matching_records = HotelBooking.objects.filter(record_locator__in=priceline_sales_ids)
        matching_records_locators = [x.record_locator for x in matching_records]

        unmatched_record_locators = set(priceline_sales_ids) - set(matching_records_locators)
        unmatched_sales_items = [UnmatchedSaleItem(x) for x in sales_data if x["sales_id"] in unmatched_record_locators]

        email_body = ""
        for item in unmatched_sales_items:
            email_body += str(item) + "\n"

        if email_body != "":
            print(self.send_email(email_body))
        else:
            print("No differences")

    def generate_endpoint(self):

        today = datetime.now().date()

        time_start = f"""{today - timedelta(days=7)}_00:00:00"""
        time_end = f"""{today}_23:59:59"""

        end_point = f"""{ENDPOINT}refid={REF_ID}&api_key={API_KEY}&time_start={time_start}&time_end={time_end}"""

        print(end_point)
        return end_point

    def get_sales_report(self):
        end_point = self.generate_endpoint()

        response = requests.get(end_point)
        response_body = json.loads(response.text)

        sales_report_data = response_body["getSharedTRK.Sales.Select.Hotel"]["results"]["sales_data"]
        return [sales_report_data[x] for x in sales_report_data.keys()]

    def send_email(self, text):
        return requests.post(
            MAIL_GUN_URL,
            auth=("api", MAIL_GUN_API_KEY),
            data={
                "from": MAIL_GUN_FROM,
                "to": "rob@simplenight.com",
                "subject": "Ghost Report - Priceline Sales Report",
                "text": text
            }
        )
