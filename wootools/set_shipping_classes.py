"""Set product shipping classes."""

import csv
import itertools
import sys

import click
from tabler import Tabler as Table

from .woocommerce_export import WoocommerceExport


class SetShippingClasses:
    """Write a CSV file to correct product shipping classes to stdout."""

    CC_SKU_COLUMN = "VAR_SKU"
    CC_RANGE_SKU_COLUMN = "RNG_SKU"
    CC_PACKAGE_TYPE_COLUMN = "OPT_Package Type"
    CC_INTERNATIONAL_SHIPPING_COLUMN = "OPT_International Shipping"

    COURIER = "Courier"
    LARGE_LETTER = "Large Letter"
    LARGE_LETTER_SINGLE = "Large Letter (Single)"
    HEAVY_AND_LARGE = "Heavy and Large"
    PACKET = "Packet"
    STANDARD = "Standard"
    EXPRESS = "Express"
    NO_INTERNATIONAL_SHIPPING = "No International Shipping"

    package_types = {
        COURIER: COURIER,
        LARGE_LETTER: LARGE_LETTER,
        LARGE_LETTER_SINGLE: LARGE_LETTER,
        HEAVY_AND_LARGE: HEAVY_AND_LARGE,
        PACKET: PACKET,
    }
    international_shipping_types = {
        STANDARD: STANDARD,
        EXPRESS: EXPRESS,
        NO_INTERNATIONAL_SHIPPING: NO_INTERNATIONAL_SHIPPING,
    }
    OUTPUT_HEADER = [WoocommerceExport.ID, WoocommerceExport.SHIPPING_CLASS]

    def __init__(self, woo_export_path, cc_export_path):
        """Write a CSV file to correct product shipping classes to stdout."""
        self.WC_export = WoocommerceExport(woo_export_path)
        self.inventory = Table(cc_export_path)
        self.WC_export.rows = [r for r in self.WC_export if r[WoocommerceExport.SKU]]
        self.existing_shipping_classes = set(
            [
                _
                for _ in self.WC_export.get_column(WoocommerceExport.SHIPPING_CLASS)
                if _
            ]
        )
        self.shipping_classes = self.get_shipping_classes()
        product_shipping_classes = self.product_shipping_classes()
        missing_skus = [
            SKU
            for SKU in self.WC_export.get_column(WoocommerceExport.SKU)
            if SKU not in product_shipping_classes
        ]
        if missing_skus:
            click.echo(missing_skus, err=True)
            raise Exception(
                "Products in Woocommerce could not be matched to Cloud Commerce products"
            )
        output_data = self.output_data(product_shipping_classes)
        self.write_status(output_data)
        self.write_output(output_data)

    @classmethod
    def get_shipping_classes(cls):
        """Return a list of valid shipping classes."""
        package_types = set(cls.package_types.values())
        international_shipping_types = set(cls.international_shipping_types.values())
        shipping_class_combinations = list(
            itertools.product(package_types, international_shipping_types)
        )
        return [cls.format_shipping_class_name(*_) for _ in shipping_class_combinations]

    @staticmethod
    def format_shipping_class_name(package_type, international_shipping):
        """Return a formatted shipping class name."""
        return " - ".join((package_type, international_shipping))

    def get_package_type_for_row(self, row):
        """Return the package type for a Cloud Commerce Product Export row."""
        SKU = row[self.CC_SKU_COLUMN]
        row_package_type = row[self.CC_PACKAGE_TYPE_COLUMN]
        if not row_package_type:
            raise Exception(f'No Package type set for "{SKU}"')
        try:
            return self.package_types[row_package_type]
        except IndexError:
            raise Exception(
                f'Unrecognized package type: "{row_package_type}" for product "{SKU}"'
            )

    def get_international_shipping_for_row(self, row):
        """Return the international shipping for a Cloud Commerce Product Export row."""
        SKU = row[self.CC_SKU_COLUMN]
        row_international_shipping = row[self.CC_INTERNATIONAL_SHIPPING_COLUMN]
        if not row_international_shipping:
            raise Exception(f'No International Shipping set for "{SKU}"')
        try:
            return self.international_shipping_types[row_international_shipping]
        except IndexError:
            raise Exception(
                (
                    "Unrecognized International Shipping: "
                    f'"{row_international_shipping}" for product "{SKU}"'
                )
            )

    def get_shipping_class_for_row(self, row):
        """Return the shipping class for a Cloud Commerce Product Export row."""
        package_type = self.get_package_type_for_row(row)
        international_shipping = self.get_international_shipping_for_row(row)
        shipping_class_name = self.format_shipping_class_name(
            package_type, international_shipping
        )
        if shipping_class_name not in self.shipping_classes:
            raise Exception(f'Invalid shipping class "{shipping_class_name}".')
        return shipping_class_name

    def product_shipping_classes(self):
        """Return a dict of {Product SKU: shipping class}."""
        product_shipping_classes = {}
        for row in self.inventory:
            shipping_class = self.get_shipping_class_for_row(row)
            product_shipping_classes[row[self.CC_SKU_COLUMN]] = shipping_class
            product_shipping_classes[row[self.CC_RANGE_SKU_COLUMN]] = shipping_class
        return product_shipping_classes

    def output_data(self, product_shipping_classes):
        """Return update CSV data as a list of lists of values."""
        data = [
            [
                row[WoocommerceExport.ID],
                product_shipping_classes[row[WoocommerceExport.SKU]],
            ]
            for row in self.WC_export
        ]
        return data

    def write_status(self, output_data):
        """Write success message to stderr."""
        click.echo(f"{len(output_data)} update rows.", err=True)

    def write_output(self, output_data):
        """Write update CSV to stdout."""
        f = csv.writer(sys.stdout)
        f.writerow(self.OUTPUT_HEADER)
        f.writerows(output_data)
