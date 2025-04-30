class ApiPricingType:
    USAGE_BASED_CHARGES = 0
    FIXED_QUOTA_CHARGES = 1
    apiPricingType) = 2

    @classmethod
    def fromValue(cls, value):
        if not value:
            raise ValueError("Empty enum value")
        try:
            return getattr(cls, value)
        except AttributeError:
            raise ValueError(f"Invalid ApiPricingType value: {value}")
