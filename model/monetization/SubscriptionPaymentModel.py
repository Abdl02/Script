class SubscriptionPaymentModel:
    def __init__(self):
        self.paymentIssueDate = None  # LocalDate  # This might be an enum
        self.paymentValueDate = None  # LocalDate  # This might be an enum
        self.amount = None  # String
        self.currency = None  # String
        self.invoiceNo = None  # String