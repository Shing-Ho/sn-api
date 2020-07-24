import unittest
from unittest.mock import patch, Mock

from api.hotel import price_verification_service
from api.tests import test_objects


class TestPriceVerificationService(unittest.TestCase):
    def test_price_verification_default_model(self):
        """Tests price verification with the default comparison model"""

        hotel = test_objects.hotel()
        original_room_rates = [test_objects.room_rate(rate_key="key1", amount="100")]
        verified_room_rates = [test_objects.room_rate(rate_key="key1", amount="100")]

        mock_adapter = Mock()
        mock_adapter.recheck.return_value = verified_room_rates

        with patch("api.hotel.adapters.adapter_service.get_adapter") as mock_get_adapter:
            mock_get_adapter.return_value = mock_adapter

        price_verification_service.recheck(hotel, original_room_rates)
