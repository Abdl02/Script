class ApiSpec:
    def __init__(self):
        self.apiSpecId = None  # String
        self.name = None  # String
        self.description = None  # String
        self.contextPath = None  # String
        self.backendServiceUrl = None  # String
        self.status = None  # ApiStatus  # This might be an enum
        self.type = None  # ApiType  # This might be an enum
        self.style = None  # ApiStyle  # This might be an enum
        self.metaData = None  # MetaData  # This might be an enum
        self.policyTemplateId = None  # String
        self.creationFlag = None  # CreationFlag  # This might be an enum
        self.addVersionToContextPath = None  # boolean
        self.authType = None  # AuthenticatorType  # This might be an enum
        self.predicates = None  # List<ApiPolicyFilter>
        self.requestPolicies = None  # Set<ApiPolicyFilter>
        self.responsePolicies = None  # Set<ApiPolicyFilter>
        self.oldVersions = None  # List<ApiSpec>
        self.apiSpecRoutes = None  # Set<ApiSpecRouteModel>
        self.revisions = None  # List<RevisionChangeModel>
        self.associatedResources = None  # List<AssociatedResource>
        self.publications = None  # List<RuntimeConfigPublicationModel>
        self.restriction = None  # RestrictionType  # This might be an enum