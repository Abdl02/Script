class ActionType:
    UNLOCK_DESIGN_MODE = "UNLOCK_DESIGN_MODE"
    RESET_REVISION = "RESET_REVISION"

    @classmethod
    def fromValue(cls, value):
        if not value:
            raise ValueError("Empty enum value")
        try:
            return getattr(cls, value)
        except AttributeError:
            raise ValueError(f"Invalid ActionType value: {value}")
