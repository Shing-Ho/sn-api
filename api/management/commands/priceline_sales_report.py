from typing import Dict

from django.core.management import BaseCommand

from api import logger

from api.hotel.adapters.priceline.priceline_sales_report import PricelineSalesReport

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
            logger.info(email_body)
        else:
            logger.warn("No differences")

