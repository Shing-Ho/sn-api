from enum import Enum

from common.exceptions import AppException


class PaymentException(AppException):
    def __init__(self, error_type, detail):
        super().__init__()
        self.error_type = error_type
        self.detail = detail


class PaymentError(Enum):
    INVALID_PAYMENT = "INVALID_PAYMENT"
    CARD_TYPE_NOT_SUPPORTED = "CARD_TYPE_NOT_SUPPORTED"
    PAYMENT_DECLINED = "PAYMENT_DECLINED"
    CARD_EXPIRED = "PAYMENT_EXPIRED"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    GENERAL = "GENERAL"
