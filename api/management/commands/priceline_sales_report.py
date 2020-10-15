from typing import Dict
from datetime import datetime, timedelta

from django.core.management import BaseCommand

from api import logger
from api.models.models import HotelBooking
from api.hotel.adapters.priceline.priceline_transport import PricelineTransport

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
            logger.info(email_body)
        else:
            logger.warn("No differences")

    def get_sales_report(self):
        sales_report = PricelineTransport()

        today = datetime.now().date()

        time_start = f"""{today - timedelta(days=7)}_00:00:00"""
        time_end = f"""{today}_23:59:59"""

        response = sales_report.sales_report(time_start=time_start, time_end=time_end)

        return response["getSharedTRK.Sales.Select.Hotel"]["results"]["sales_data"]
