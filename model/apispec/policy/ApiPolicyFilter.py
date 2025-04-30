class ApiPolicyFilter:
    def __init__(self):
        self.policyDefinitionId = None  # Long
        self.args = None  # Map<String, String>
        self.httpExchange = None  # HttpExchange  # This might be an enum
        self.policyName = None  # ExchangePolicyName  # This might be an enum
        self.policyDescription = None  # String
        self.order = None  # Long
        self.createDate = None  # LocalDateTime
        self.lastUpdate = None  # LocalDateTime