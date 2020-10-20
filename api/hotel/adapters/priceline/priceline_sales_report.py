
from datetime import datetime, timedelta

from api.hotel.adapters.priceline.priceline_transport import PricelineTransport
from api.models.models import HotelBooking


class PricelineSalesReport(PricelineTransport):
    def __init__(self):
        super().__init__()

    def get_sales_report(self):
        sales_report = PricelineTransport()

        today = datetime.now().date()

        time_start = f"""{today - timedelta(days=7)}_00:00:00"""
        time_end = f"""{today}_23:59:59"""

        response = sales_report.sales_report(time_start=time_start, time_end=time_end)

        return response["getSharedTRK.Sales.Select.Hotel"]["results"]["sales_data"]

    def find_unmatched_bookings(self):
        sales_data = self.get_sales_report()

        priceline_sales_ids = [x["sales_id"] for x in sales_data]

        matching_records = HotelBooking.objects.filter(record_locator__in=priceline_sales_ids)

        matching_records_locators = [x.record_locator for x in matching_records]
        unmatched_record_locators = set(priceline_sales_ids) - set(matching_records_locators)

        unmatched_sales_items = [x for x in sales_data if x["sales_id"] in unmatched_record_locators]
        return unmatched_sales_items
