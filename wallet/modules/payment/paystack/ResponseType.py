from typing import TypedDict


class InitializationResponse(TypedDict):
    authorization_url: str
    access_code: str
    reference: str


class ChargeAuthorization(TypedDict):
    authorization_code: str
    bin: str
    last4: str
    exp_month: str
    exp_year: str
    channel: str
    card_type: str
    bank: str
    country_code: str
    brand: str
    reusable: bool
    signature: str


class ChargeResponse(TypedDict):
    # custom success indicator
    paid: bool
    # paystack response
    reference: str
    amount: int
    currency: str
    transaction_date: str
    message: str
    status: str
    domain: str  # "test" or "live"
    gateway_response: str
    channel: str
    authorization: ChargeAuthorization
