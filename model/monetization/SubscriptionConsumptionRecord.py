class SubscriptionConsumptionRecord:
    def __init__(self):
        self.envId = None  # String
        self.envType = None  # EnvironmentType  # This might be an enum
        self.envName = None  # String
        self.consumerKey = None  # String
        self.planId = None  # Long
        self.projectId = None  # Long
        self.subscriptionId = None  # Long
        self.productId = None  # Long
        self.productsConsumptionsDetails = None  # List<ProductConsumptionDetails>
        self.consumptionPeriod = None  # Long