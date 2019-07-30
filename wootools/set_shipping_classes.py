"""Set product shipping classes."""

from .exceptions import ProductNotFoundInCloudCommerceExport
from .product_update import ProductUpdateWithCloudCommerceExport
from .woocommerce_export import WoocommerceExport


class PackageTypes:
    """Cloud Commerce Package Types."""

    PACKET = "Packet"
    LARGE_LETTER = "Large Letter"
    LARGE_LETTER_SINGLE = "Large Letter (Single)"
    HEAVY_AND_LARGE = "Heavy and Large"
    COURIER = "Courier"
    ALL = [PACKET, LARGE_LETTER, LARGE_LETTER_SINGLE, HEAVY_AND_LARGE, COURIER]


class InternationalShipping:
    """Cloud Commerce International Shipping."""

    STANDARD = None
    EXPRESS = "Express"
    NO_INTERNATIONAL_SHIPPING = "No International Shipping"
    ALL = [STANDARD, EXPRESS, NO_INTERNATIONAL_SHIPPING]


class ShippingClasses:
    """Woocommerce Shipping Classes."""

    STANDARD = ""
    HEAVY = "Heavy"
    ALL = [STANDARD, HEAVY]


class SetShippingClasses(ProductUpdateWithCloudCommerceExport):
    """Write a CSV file to correct product shipping classes to stdout."""

    IMPORT_HEADER = [WoocommerceExport.ID, WoocommerceExport.SHIPPING_CLASS]

    def process_export_row(self, row):
        """Return a CSV row to update the shipping class if necessary, otherwise None."""
        sku = row[WoocommerceExport.SKU]
        if not sku:
            return None
        package_types = self.get_package_types(sku)
        shipping_class = self.get_shipping_class(*package_types)
        if row[WoocommerceExport.SHIPPING_CLASS] == shipping_class:
            return None
        return [row[WoocommerceExport.ID], shipping_class]

    @staticmethod
    def get_shipping_class(package_type, international_shipping):
        """Return the appropriate shipping class for a package type and international shipping."""
        heavy_package_types = [PackageTypes.HEAVY_AND_LARGE, PackageTypes.COURIER]
        heavy_international_shipping = [
            InternationalShipping.EXPRESS,
            InternationalShipping.NO_INTERNATIONAL_SHIPPING,
        ]
        if (
            package_type in heavy_package_types
            or international_shipping in heavy_international_shipping
        ):
            return ShippingClasses.HEAVY
        return ShippingClasses.STANDARD

    @staticmethod
    def format_shipping_class_name(package_type, international_shipping):
        """Return a formatted shipping class name."""
        return " - ".join((package_type, international_shipping))

    def get_package_type(self, row):
        """Return the package type for a Cloud Commerce Product Export row."""
        SKU = row[self.CC_SKU_COLUMN]
        package_type = row[self.CC_PACKAGE_TYPE_COLUMN]
        if not package_type:
            raise Exception(f'No Package type set for "{SKU}"')
        return package_type

    def get_international_shipping(self, row):
        """Return the international shipping for a Cloud Commerce Product Export row."""
        SKU = row[self.CC_SKU_COLUMN]
        international_shipping = row[self.CC_INTERNATIONAL_SHIPPING_COLUMN]
        if not international_shipping:
            raise Exception(f'No International Shipping set for "{SKU}"')
        return international_shipping

    def get_package_types(self, SKU):
        """Return the pacage types for a product."""
        try:
            cc_row = self.CC_ROWS[SKU]
        except KeyError:
            raise ProductNotFoundInCloudCommerceExport(SKU)
        return (self.get_package_type(cc_row), self.get_international_shipping(cc_row))
