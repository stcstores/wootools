"""Product Update is the base class for producing update CSV files."""

import csv
import sys

import click
from tabler import Table

from .woocommerce_export import WoocommerceExport


def create_update_file(update_class, *args, **kwargs):
    """Create a product update CSV."""
    update = update_class(*args, **kwargs)
    data = update.import_data
    if data:
        update.write_output()
        update.write_success_message()
    else:
        update.write_empty_message()


class ProductUpdate:
    """Base class for producing update CSV files."""

    def __init__(self, export_file_path):
        """Write a CSV file to make the necessary changes to stdout."""
        self.export = WoocommerceExport(export_file_path)
        self.import_data = self.create_import_data(self.export)

    def process_export_row(self, row):
        """Return an updated CSV row if updates are necessary, otherwise return None."""
        raise NotImplementedError

    def create_import_data(self, export):
        """Return CSV rows as a list of lists of values."""
        import_data = []
        for export_row in export:
            import_row = self.process_export_row(export_row)
            if import_row is not None:
                import_data.append(import_row)
        return import_data

    def write_success_message(self):
        """Write status message to sdterr."""
        click.echo(f"{len(self.import_data)} update rows.", err=True)

    def write_empty_message(self):
        """Write messsage for an empty output to stderr."""
        click.echo("No data to write.", err=True)

    def write_output(self):
        """Write CSV to stdout."""
        f = csv.writer(sys.stdout)
        f.writerow(self.IMPORT_HEADER)
        f.writerows(self.import_data)


class ProductUpdateWithCloudCommerceExport(ProductUpdate):
    """Base class for producing update CSV files referencing a Cloud Commerce product export."""

    CC_SKU_COLUMN = "VAR_SKU"
    CC_RANGE_SKU_COLUMN = "RNG_SKU"
    CC_PACKAGE_TYPE_COLUMN = "OPT_Package Type"
    CC_INTERNATIONAL_SHIPPING_COLUMN = "OPT_International Shipping"

    def __init__(self, woo_export_path, cc_export_path):
        """Get a lookup table for Cloud Commerce Product Export rows."""
        self.inventory = Table(cc_export_path)
        self.CC_ROWS = {}
        for row in self.inventory:
            self.CC_ROWS[row["VAR_SKU"]] = row
            self.CC_ROWS[row["RNG_SKU"]] = row
        super().__init__(woo_export_path)
