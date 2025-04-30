class ProductSimpleViewModel:
    def __init__(self):
        self.productId = None  # Long
        self.name = None  # String
        self.desc = None  # String
        self.status = None  # ProductStatus  # This might be an enum