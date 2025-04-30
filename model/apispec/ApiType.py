class ApiType:
    PUBLIC = 0
    PRIVATE = 1
    PARTNER = 2
    type) = 3

    @classmethod
    def fromValue(cls, value):
        if not value:
            raise ValueError("Empty enum value")
        try:
            return getattr(cls, value)
        except AttributeError:
            raise ValueError(f"Invalid ApiType value: {value}")
