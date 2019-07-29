"""
FixCategories updates category information.

It removes the Uncategorized category from products with any other category and
adds Uncategorized to any products with no category.
"""

import csv
import sys

import click

from .woocommerce_export import WoocommerceExport


class FixCategories:
    """
    FixCategories updates category information.

    It removes the Uncategorized category from products with any other category and
    adds Uncategorized to any products with no category.
    """

    UNCATEGORIZED = "Uncategorized"
    IMPORT_HEADER = [WoocommerceExport.ID, WoocommerceExport.CATEGORIES]

    def __init__(self, export_file_path):
        """Write a CSV file to make the necessary changes to stdout."""
        self.export = WoocommerceExport(export_file_path)
        output_data = self.create_import_data()
        self.write_status(output_data)
        self.write_output(output_data)

    def add_uncategorized(self, categories):
        """Add Uncategorized to categories if it is an empty list."""
        if len(categories) == 0:
            categories = [self.UNCATEGORIZED]
        return categories

    def remove_uncategorized(self, categories):
        """Remove Uncategroized from categories if it contains other categories."""
        if self.UNCATEGORIZED in categories and len(categories) > 1:
            categories = [_ for _ in categories if _ != self.UNCATEGORIZED]
        return categories

    def parse_categories(self, category_column_contents):
        """Return an export categories field as a list of categories."""
        return [_.strip() for _ in category_column_contents.split(",")]

    def format_categories(self, categories):
        """Return a list of categories formatted for a Woocommerce CSV file."""
        return ", ".join(categories)

    def process_export_row(self, row):
        """Return an  updated CSV row if updates are necessary, otherwise return None."""
        current_categories = self.parse_categories(row[self.export.CATEGORIES])
        non_empty_categories = self.add_uncategorized(current_categories)
        fixed_categories = self.remove_uncategorized(non_empty_categories)
        if fixed_categories != current_categories:
            return [row[self.export.ID], self.format_categories(fixed_categories)]
        return None

    def create_import_data(self):
        """Return CSV rows as a list of lists of values."""
        import_data = []
        for export_row in self.export:
            import_row = self.process_export_row(export_row)
            if import_row is not None:
                import_data.append(import_row)
        return import_data

    def write_status(self, output_data):
        """Write status message to sdterr."""
        click.echo(f"{len(output_data)} update rows.", err=True)

    def write_output(self, import_data):
        """Write CSV to stdout."""
        f = csv.writer(sys.stdout)
        f.writerow(self.IMPORT_HEADER)
        f.writerows(import_data)
