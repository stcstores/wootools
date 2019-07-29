"""AddDisclaimers adds disclaimers to the descriptions of products in the knives category."""

import csv
import sys

import click

from .woocommerce_export import WoocommerceExport


class AddDisclaimers:
    """AddDisclaimers adds disclaimers to the descriptions of products in the knives category."""

    UNCATEGORIZED = "Uncategorized"
    IMPORT_HEADER = [WoocommerceExport.ID, WoocommerceExport.CATEGORIES]

    disclaimer_categories = ["Knives"]
    header = "DISCLAIMER:"
    disclaimer = "\\n".join(
        [
            "<br>",
            f"<p>{header}</p>",
            "<p>You must be 18 years or older in order to purchase this product.</p>",
            (
                "<p>It is the buyers obligation that they ensure they know their states "
                "rules and regulation in regards to knives and to make sure they are "
                "not breaking the law by purchasing knives.</p>"
            ),
            (
                "<p>By purchasing from this website and you agree that you are 18 years "
                "or older and understand rules and regulations in relation to knives in "
                "your own state or territory.</p>"
            ),
        ]
    )

    def __init__(self, export_file_path):
        """Write a CSV file to make the necessary changes to stdout."""
        self.export = WoocommerceExport(export_file_path)
        output_data = self.create_import_data()
        self.write_status(output_data)
        self.write_output(output_data)

    def process_export_row(self, row):
        """Return an update row if an update is required, otherwise return None."""
        if any(_ in row[self.export.CATEGORIES] for _ in self.disclaimer_categories):
            description = self.add_disclaimer(row[self.export.DESCRIPTION])
            if description is not None:
                return [row[self.export.ID], description]
        return None

    def add_disclaimer(self, description):
        """Add the disclaimer to a description."""
        if self.header not in description:
            clean_description = self.clean_description(description)
            updated_description = clean_description + self.disclaimer
            return updated_description
        return None

    def clean_description(self, description):
        """Return the description with properly formatted newlines."""
        return description.replace("\n", "\\n")

    def create_import_data(self):
        """Return the update CSV as lists of row data."""
        import_data = []
        for export_row in self.export:
            import_row = self.process_export_row(export_row)
            if import_row is not None:
                import_data.append(import_row)
        return import_data

    def write_status(self, output_data):
        """Write completion message to stderr."""
        click.echo(f"{len(output_data)} update rows.", err=True)

    def write_output(self, import_data):
        """Write the update CSV to stdout."""
        f = csv.writer(sys.stdout)
        f.writerow(self.IMPORT_HEADER)
        f.writerows(import_data)
