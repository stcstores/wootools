"""Set product shipping classes."""

import csv
import sys

import click
from tabler import Tabler as Table

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


class SetShippingClasses:
    """Write a CSV file to correct product shipping classes to stdout."""

    CC_SKU_COLUMN = "VAR_SKU"
    CC_RANGE_SKU_COLUMN = "RNG_SKU"
    CC_PACKAGE_TYPE_COLUMN = "OPT_Package Type"
    CC_INTERNATIONAL_SHIPPING_COLUMN = "OPT_International Shipping"

    OUTPUT_HEADER = [WoocommerceExport.ID, WoocommerceExport.SHIPPING_CLASS]

    def __init__(self, woo_export_path, cc_export_path):
        """Write a CSV file to correct product shipping classes to stdout."""
        self.WC_export = WoocommerceExport(woo_export_path)
        self.inventory = Table(cc_export_path)
        self.WC_export.rows = [r for r in self.WC_export if r[WoocommerceExport.SKU]]
        self.shipping_class_lookup = self.product_shipping_classes()
        missing_skus = [
            SKU
            for SKU in self.WC_export.get_column(WoocommerceExport.SKU)
            if SKU not in self.shipping_class_lookup
        ]
        if missing_skus:
            click.echo(missing_skus, err=True)
            raise Exception(
                "Products in Woocommerce could not be matched to Cloud Commerce products"
            )
        output_data = self.output_data()
        self.write_status(output_data)
        self.write_output(output_data)

    @staticmethod
    def format_shipping_class_name(package_type, international_shipping):
        """Return a formatted shipping class name."""
        return " - ".join((package_type, international_shipping))

    def get_package_type_for_row(self, row):
        """Return the package type for a Cloud Commerce Product Export row."""
        SKU = row[self.CC_SKU_COLUMN]
        package_type = row[self.CC_PACKAGE_TYPE_COLUMN]
        if not package_type:
            raise Exception(f'No Package type set for "{SKU}"')
        return package_type

    def get_international_shipping_for_row(self, row):
        """Return the international shipping for a Cloud Commerce Product Export row."""
        SKU = row[self.CC_SKU_COLUMN]
        international_shipping = row[self.CC_INTERNATIONAL_SHIPPING_COLUMN]
        if not international_shipping:
            raise Exception(f'No International Shipping set for "{SKU}"')
        return international_shipping

    def get_shipping_class_for_row(self, row):
        """Return the shipping class for a Cloud Commerce Product Export row."""
        package_type = self.get_package_type_for_row(row)
        international_shipping = self.get_international_shipping_for_row(row)
        return self.get_shipping_class(package_type, international_shipping)

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

    def product_shipping_classes(self):
        """Return a dict of {Product SKU: shipping class}."""
        product_shipping_classes = {}
        for row in self.inventory:
            shipping_class = self.get_shipping_class_for_row(row)
            product_shipping_classes[row[self.CC_SKU_COLUMN]] = shipping_class
            product_shipping_classes[row[self.CC_RANGE_SKU_COLUMN]] = shipping_class
        return product_shipping_classes

    def get_update_row(self, row):
        """Return a CSV row to update the shipping class if necessary, otherwise None."""
        shipping_class = self.shipping_class_lookup[row[WoocommerceExport.SKU]]
        if row[WoocommerceExport.SHIPPING_CLASS] == shipping_class:
            return None
        return [row[WoocommerceExport.ID], shipping_class]

    def output_data(self):
        """Return update CSV data as a list of lists of values."""
        data = []
        for row in self.WC_export:
            update_row = self.get_update_row(row)
            if update_row is not None:
                data.append(update_row)
        return data

    def write_status(self, output_data):
        """Write success message to stderr."""
        click.echo(f"{len(output_data)} update rows.", err=True)

    def write_output(self, output_data):
        """Write update CSV to stdout."""
        f = csv.writer(sys.stdout)
        f.writerow(self.OUTPUT_HEADER)
        f.writerows(output_data)
