class ApiStatus:
    DRAFT = 0
    PUBLISHED = 1
    UNPUBLISHED = 2
    DELETED = 3
    status) = 4

    @classmethod
    def fromValue(cls, value):
        if not value:
            raise ValueError("Empty enum value")
        try:
            return getattr(cls, value)
        except AttributeError:
            raise ValueError(f"Invalid ApiStatus value: {value}")
