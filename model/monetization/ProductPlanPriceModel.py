class represents:
    def __init__(self):
        self.id = None  # Long
        self.product = None  # ProductSimpleViewModel  # This might be an enum
        self.plan = None  # PlanSimpleViewModel  # This might be an enum
        self.planName = None  # String
        self.subscriptionPeriodOptions = None  # Set<SubscriptionPeriodOption>
        self.renewalTypeOptions = None  # Set<SubscriptionRenewalType>
        self.priceType = None  # ApiPricingType  # This might be an enum
        self.monthlyPrice = None  # BigDecimal  # This might be an enum
        self.yearlyPrice = None  # BigDecimal  # This might be an enum
        self.lifetimePrice = None  # BigDecimal  # This might be an enum
        self.apiCallsQuota = None  # Long
        self.timeUnit = None  # TimeUnit  # This might be an enum
        self.missingProductNames = None  # Set<String>