"""Wootools exceptions."""


class ProductNotFoundInCloudCommerceExport(Exception):
    """Exception for failure to find a Woocommerce product in a Cloud Commerce export."""

    def __init__(self, SKU):
        """Raise exception."""
        self.SKU = SKU
        super().__init__(
            f"The product with SKU {SKU} was not found in the Cloud Commerce Export."
        )
