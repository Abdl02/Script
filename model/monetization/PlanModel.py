class PlanModel:
    def __init__(self):
        self.planId = None  # Long
        self.definitionType = None  # PlanDefinitionType  # This might be an enum
        self.name = None  # String
        self.desc = None  # String
        self.premium = None  # boolean
        self.productPlanPrices = None  # Set<ProductPlanPriceModel>
        self.priceType = None  # ApiPricingType  # This might be an enum
        self.planStatus = None  # PlanStatus  # This might be an enum
        self.renewalTypeOptions = None  # Set<SubscriptionRenewalType>
        self.subscriptionPeriodOptions = None  # Set<SubscriptionPeriodOption>
        self.associatedResources = None  # List<AssociatedResource>
        self.publications = None  # List<RuntimeConfigPublicationModel>
        self.createAt = None  # LocalDateTime
        self.lastUpdateAt = None  # LocalDateTime
        self.restriction = None  # RestrictionType  # This might be an enum