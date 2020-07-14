import unittest
import uuid
from datetime import date

from api.hotel.adapters.stub.stub import StubHotelAdapter
from api.hotel.hotels import (
    HotelSpecificSearch,
    RoomOccupancy,
    HotelBookingRequest,
    Customer,
    Traveler,
    RoomRate,
    Payment,
    Money,
    PaymentCardParameters,
    CardType, Address,
)


class TestStubHotelAdapter(unittest.TestCase):
    def test_search_by_hotel_id(self):
        search_request = HotelSpecificSearch(
            hotel_id="A1H2J6",
            checkin_date=date(2020, 1, 20),
            checkout_date=date(2020, 1, 27),
            occupancy=RoomOccupancy(2, 1),
        )

        stub_adapter = StubHotelAdapter()
        response = stub_adapter.search_by_id(search_request)

        self.assertIsNotNone(response.hotel_id)
        self.assertIsNotNone(response.checkin_date)
        self.assertIsNotNone(response.checkin_date)
        self.assertIsNotNone(response.occupancy)
        self.assertIsNotNone(response.room_types)
        self.assertIsNotNone(response.room_types[0].bed_types)
        self.assertIsNotNone(response.room_types[0].amenities)
        self.assertIsNotNone(response.room_types[0].photos)
        self.assertIsNotNone(response.room_types[0].rates)
        self.assertIsNotNone(response.room_types[0].rates[0].description)
        self.assertIsNotNone(response.room_types[0].rates[0].total)
        self.assertIsNotNone(response.room_types[0].rates[0].total_tax_rate)
        self.assertIsNotNone(response.room_types[0].rates[0].total_base_rate)
        self.assertIsNotNone(response.room_types[0].rates[0].daily_rates)
        self.assertIsNotNone(response.room_types[0].rates[0].daily_rates[0].total)
        self.assertIsNotNone(response.room_types[0].rates[0].daily_rates[0].tax)
        self.assertIsNotNone(response.room_types[0].rates[0].daily_rates[0].base_rate)

    def test_booking(self):
        customer = Customer(
            first_name="John",
            last_name="Smith",
            phone_number="+1 (555) 867-5309",
            email="john.smith@gmail.com",
            country="US",
        )

        traveler = Traveler(first_name="Jane", last_name="Smith", occupancy=RoomOccupancy(adults=1, children=0))
        room_rate = RoomRate(
            description="King Bed Oceanview Suite",
            additional_detail=list(),
            total_base_rate=Money(526.22, "USD"),
            total_tax_rate=Money(63.29, "USD"),
            total=Money(589.51, "USD"),
        )

        payment_card_params = PaymentCardParameters(
            card_type=CardType.VI,
            card_number="4111111111111111",
            cardholder_name="John Q. Smith",
            expiration_month="05",
            expiration_year="25",
            cvv="123",
        )

        address = Address("San Francisco", "CA", "94111", "US", "120 Market Street")
        payment = Payment(payment_card_params, billing_address=address)

        booking_request = HotelBookingRequest(
            api_version=1,
            transaction_id=str(uuid.uuid4()),
            hotel_id="HAUE1X",
            checkin=date(2020, 2, 15),
            checkout=date(2020, 2, 20),
            language="en_US",
            customer=customer,
            traveler=traveler,
            room_rate=room_rate,
            payment=payment,
            tracking=str(uuid.uuid4()),
            ip_address="1.1.1.1"
        )

        stub_adapter = StubHotelAdapter()
        response = stub_adapter.booking(booking_request)
        print(response)

        self.assertEqual(1, response.api_version)
        self.assertIsNotNone(response.transaction_id)
        self.assertTrue(response.status.success)
        self.assertIsNotNone(response.reservation)
        self.assertIsNotNone(response.reservation.locator.id)
        self.assertIsNotNone(response.reservation.hotel_locator.id)
        self.assertIsNotNone(response.reservation.hotel_id)
        self.assertEqual("2020-02-15", str(response.reservation.checkin))
        self.assertEqual("2020-02-20", str(response.reservation.checkout))
        self.assertEqual("John", response.reservation.customer.first_name)
        self.assertEqual("Smith", response.reservation.customer.last_name)
        self.assertEqual("+1 (555) 867-5309", response.reservation.customer.phone_number)
        self.assertIsNotNone("john.smith@gmail.com", response.reservation.customer.email)
        self.assertEqual("Jane", response.reservation.traveler.first_name)
        self.assertEqual("Smith", response.reservation.traveler.last_name)
        self.assertEqual(1, response.reservation.traveler.occupancy.adults)
        self.assertEqual("King Bed Oceanview Suite", response.reservation.room_rate.description)
        self.assertEqual(526.22, response.reservation.room_rate.total_base_rate.amount)
        self.assertEqual(63.29, response.reservation.room_rate.total_tax_rate.amount)
        self.assertEqual(589.51, response.reservation.room_rate.total.amount)
