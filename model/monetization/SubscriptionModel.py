class SubscriptionModel:
    def __init__(self):
        self.subscriptionId = None  # Long
        self.project = None  # ProjectModel  # This might be an enum
        self.status = None  # SubscriptionStatus  # This might be an enum
        self.renewalType = None  # SubscriptionRenewalType  # This might be an enum
        self.subscriptionPeriod = None  # SubscriptionPeriodOption  # This might be an enum
        self.trial = None  # boolean
        self.plan = None  # PlanModel  # This might be an enum
        self.subscriptionConsumptionRecord = None  # List<SubscriptionConsumptionRecord>
        self.publications = None  # List<RuntimeConfigPublicationModel>
        self.restriction = None  # RestrictionType  # This might be an enum
        self.source = None  # Source  # This might be an enum
        self.startDate = None  # LocalDate  # This might be an enum
        self.endDate = None  # LocalDate  # This might be an enum
        self.nextBillingDate = None  # LocalDate  # This might be an enum
        self.lastBillingDate = None  # LocalDate  # This might be an enum
        self.nextBillingAmount = None  # String
        self.lastBillingAmount = None  # String
        self.lastRenewalDate = None  # LocalDate  # This might be an enum
        self.nextRenewalDate = None  # LocalDate  # This might be an enum
        self.cancellationDate = None  # LocalDate  # This might be an enum
        self.paymentMethod = None  # String
        self.payments = None  # Set<SubscriptionPaymentModel>