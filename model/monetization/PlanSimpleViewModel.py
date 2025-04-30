class PlanSimpleViewModel:
    def __init__(self):
        self.planId = None  # Long
        self.name = None  # String
        self.desc = None  # String
        self.subscriptionPeriodOptions = None  # Set<SubscriptionPeriodOption>
        self.sandboxPlan = None  # boolean
        self.definitionType = None  # PlanDefinitionType  # This might be an enum