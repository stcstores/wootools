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


class Categories:
    """Shipping classes based on product category."""

    KNIFE = "Knife"
    KNIVES = "Sports and Leisure > Knives"
    categories = {KNIVES: KNIFE}


class SetShippingClasses(ProductUpdateWithCloudCommerceExport):
    """Write a CSV file to correct product shipping classes to stdout."""

    IMPORT_HEADER = [WoocommerceExport.ID, WoocommerceExport.SHIPPING_CLASS]

    @classmethod
    def process_export_row(cls, row, lookup):
        """Return a CSV row to update the shipping class if necessary, otherwise None."""
        sku = row[WoocommerceExport.SKU]
        if not sku:
            return None
        package_types = cls.get_package_types(sku, lookup)
        existing_shipping_class = row[WoocommerceExport.SHIPPING_CLASS]
        categories = row[WoocommerceExport.CATEGORIES].split(",")
        category = row[WoocommerceExport.CATEGORIES]
        shipping_class = None
        for category in categories:
            if category in Categories.categories:
                shipping_class = Categories.categories[category]
        if shipping_class is None:
            shipping_class = cls.get_shipping_class(*package_types)
        if shipping_class == existing_shipping_class:
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

    @classmethod
    def get_package_type(cls, row):
        """Return the package type for a Cloud Commerce Product Export row."""
        SKU = row[cls.CC_SKU_COLUMN]
        package_type = row[cls.CC_PACKAGE_TYPE_COLUMN]
        if not package_type:
            raise Exception(f'No Package type set for "{SKU}"')
        return package_type

    @classmethod
    def get_international_shipping(cls, row):
        """Return the international shipping for a Cloud Commerce Product Export row."""
        SKU = row[cls.CC_SKU_COLUMN]
        international_shipping = row[cls.CC_INTERNATIONAL_SHIPPING_COLUMN]
        if not international_shipping:
            raise Exception(f'No International Shipping set for "{SKU}"')
        return international_shipping

    @classmethod
    def get_package_types(cls, SKU, lookup):
        """Return the pacage types for a product."""
        try:
            if "RNG" in SKU:
                SKU = "_".join(SKU.split("_")[:2])
            else:
                SKU = SKU.split("_")[0]
            cc_row = lookup[SKU]
        except KeyError:
            raise ProductNotFoundInCloudCommerceExport(SKU)
        return (cls.get_package_type(cc_row), cls.get_international_shipping(cc_row))
