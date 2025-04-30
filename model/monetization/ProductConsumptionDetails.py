class ProductConsumptionDetails:
    def __init__(self):
        self.productId = None  # Long
        self.productName = None  # String
        self.apiCallsTotal = None  # Long
        self.remainingHit = None  # Long
        self.consumption = None  # Long
        self.price = None  # BigDecimal  # This might be an enum