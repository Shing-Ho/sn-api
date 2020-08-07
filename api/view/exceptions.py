from rest_framework.views import exception_handler

from common.exceptions import AppException


def handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response, and handle specific API errors
    if response is not None:
        response.data["status_code"] = response.status_code
        if isinstance(exc, BookingException):
            del response.data["detail"]
            response.data["error"] = {}
            response.data["error"]["type"] = exc.error_type.value
            response.data["error"]["message"] = exc.detail

    return response


class BookingException(AppException):
    def __init__(self, error_type, detail):
        super().__init__()
        self.error_type = error_type
        self.detail = detail


class PaymentException(BookingException):
    pass
