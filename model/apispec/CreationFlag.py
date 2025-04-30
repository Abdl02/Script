class CreationFlag:
    ADDED = 0
    IMPORTED = 1

    @classmethod
    def fromValue(cls, value):
        if not value:
            raise ValueError("Empty enum value")
        try:
            return getattr(cls, value)
        except AttributeError:
            raise ValueError(f"Invalid CreationFlag value: {value}")
