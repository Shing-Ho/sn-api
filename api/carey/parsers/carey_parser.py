from typing import List
from api.carey.models.carey_api_model import (
    QuoteResponse,
    VehicleDetails,
    ChargeDetails,
    ChargeItem,
    Reference,
    TotalAmount,
    AdditionalInfo,
)


class CareyParser:
    def __init__(self):
        super().__init__()

    # def parse_quotes(self, quotes_data):
    def parse_quotes(self, quotes_datas) -> List[QuoteResponse]:
        quote_details = []

        for quote_data in quotes_datas:
            chargeItemsDetails = quote_data["Reference"]["TPA_Extensions"]["ChargeDetails"]["Charges"]["Items"][
                "ItemVariable"
            ]
            chargeItemsInfo = []
            for chargeItemsDetail in chargeItemsDetails:
                chargeItemInfo = ChargeItem(
                    itemName=chargeItemsDetail["ItemName"],
                    itemDescription=chargeItemsDetail["ItemDescription"],
                    itemUnit=chargeItemsDetail["ItemUnit"]["Unit"],
                    itemUnitValue=chargeItemsDetail["ItemUnit"]["_value_1"],
                    itemUnitPrice=chargeItemsDetail["ItemUnitPrice"]["_value_1"],
                    itemUnitPriceCurrency=chargeItemsDetail["ItemUnitPrice"]["Currency"],
                    readBack=chargeItemsDetail["ReadBack"],
                    sequenceNumber=chargeItemsDetail["SequenceNumber"],
                )
                chargeItemsInfo.append(chargeItemInfo)

            quote_detail = QuoteResponse(
                vehicleDetails=VehicleDetails(
                    vehicleName=quote_data["Shuttle"][0]["Vehicle"]["Type"]["_value_1"],
                    vehicleCode=quote_data["Shuttle"][0]["Vehicle"]["Type"]["Description"],
                    vehicleDescriptionDetail=quote_data["Shuttle"][0]["Vehicle"]["Type"]["DescriptionDetail"],
                    maxPassengers=quote_data["Shuttle"][0]["Vehicle"]["VehicleSize"]["MaxPassengerCapacity"],
                    maxBags=quote_data["Shuttle"][0]["Vehicle"]["VehicleSize"]["MaxBaggageCapacity"],
                ),
                chargeDetails=ChargeDetails(
                    readBack=quote_data["Reference"]["TPA_Extensions"]["ChargeDetails"]["Charges"]["ReadBack"],
                    billingType=quote_data["Reference"]["TPA_Extensions"]["ChargeDetails"]["Charges"]["BillingType"],
                ),
                chargeItems=chargeItemsInfo,
                reference=Reference(
                    estimatedDistance=quote_data["Reference"]["TPA_Extensions"]["EstimatedDistance"],
                    estimatedTime=quote_data["Reference"]["TPA_Extensions"]["EstimatedTime"],
                ),
                total=TotalAmount(
                    totalAmountValue=quote_data["TotalCharge"]["RateTotalAmount"],
                    totalAmountCurrency=quote_data["Reference"]["TPA_Extensions"]["TotalAmount"]["Currency"],
                    totalAmountDescription=quote_data["Reference"]["TPA_Extensions"]["TotalAmount"]["_value_1"],
                ),
                additional=AdditionalInfo(
                    notice=quote_data["Reference"]["TPA_Extensions"]["Notice"],
                    garageToGarageEstimate=quote_data["Reference"]["TPA_Extensions"]["GarageToGarageEstimate"],
                ),
            )

            quote_details.append(quote_detail)

        return quote_details

    # def _process_activities(activities: List[AdapterActivity]) -> List[SimplenightActivity]:
