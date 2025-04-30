class ProductModel:
    def __init__(self):
        self.productId = None  # Long
        self.name = None  # String
        self.desc = None  # String
        self.status = None  # ProductStatus  # This might be an enum
        self.segment = None  # String
        self.version = None  # String
        self.createdAt = None  # LocalDateTime
        self.lastUpdatedAt = None  # LocalDateTime
        self.premium = None  # boolean
        self.restriction = None  # RestrictionType  # This might be an enum
        self.availableOnDevPortal = None  # boolean
        self.publishedOnProd = None  # boolean
        self.apiSpecs = None  # List<ApiSpec>
        self.productPlanPrices = None  # Set<ProductPlanPriceModel>
        self.associatedResources = None  # List<AssociatedResource>
        self.publications = None  # List<RuntimeConfigPublicationModel>