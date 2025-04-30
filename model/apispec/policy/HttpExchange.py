class HttpExchange:
    REQUEST = 0
    RESPONSE = 1
    SYSTEM_REQUEST = 2
    SYSTEM_RESPONSE = 3
    httpExchange) = 4

    @classmethod
    def fromValue(cls, value):
        if not value:
            raise ValueError("Empty enum value")
        try:
            return getattr(cls, value)
        except AttributeError:
            raise ValueError(f"Invalid HttpExchange value: {value}")
