class ExchangePolicyName:
    REQUEST_QUOTA = 0
    COPY_REQUEST_HEADER = 1
    ADD_REQUEST_HEADER = 2
    COPY_REQUEST_QUERY_PARAM = 3
    ADD_REQUEST_QUERY_PARAM = 4
    JWS_VERIFICATION = 5
    MONETIZATION = 6
    REQUEST_BODY_MODIFIER = 7
    JSON_TO_JSON_REQUEST_TRANSFORMER = 8
    JWS_REQUEST_HEADER_VERIFIER = 9
    BACKEND_SERVICE_AUTH = 10
    MOCK_RESPONSE = 11
    JSON_TO_JSON_RESPONSE_TRANSFORMER = 12
    RESPONSE_BODY_MODIFIER = 13
    FLATTEN_JSON_RESPONSE = 14
    JWS_RESPONSE_HEADER_GENERATOR = 15

    @classmethod
    def fromValue(cls, value):
        if not value:
            raise ValueError("Empty enum value")
        try:
            return getattr(cls, value)
        except AttributeError:
            raise ValueError(f"Invalid ExchangePolicyName value: {value}")
