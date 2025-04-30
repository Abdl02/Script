class ApiStyle:
    REST = 0
    SOAP = 1
    WEB_SOCKET = 2
    GRPC = 3
    type) = 4

    @classmethod
    def fromValue(cls, value):
        if not value:
            raise ValueError("Empty enum value")
        try:
            return getattr(cls, value)
        except AttributeError:
            raise ValueError(f"Invalid ApiStyle value: {value}")
