"""WoocommerceExport holds Woocommerce export CSV data."""
import csv


class _WoocommerceExportRow:
    def __init__(self, row, export):
        self.export = export
        self.row = row

    def __getitem__(self, index):
        return self.row[self.export.header.index(index)]


class WoocommerceExport:
    """WoocommerceExport holds Woocommerce export CSV data."""

    ID = "ID"
    SKU = "SKU"
    CATEGORIES = "Categories"
    SHIPPING_CLASS = "Shipping class"
    PRICE = "Regular price"
    DESCRIPTION = "Description"

    def __init__(self, file_path):
        """Read an export CSV and create the header and rows."""
        with open(file_path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)

        self.header = rows[0]
        self.rows = [_WoocommerceExportRow(row, self) for row in rows[1:]]

    def __getitem__(self, index):
        return self.rows[index]

    def __iter__(self):
        for _ in self.rows:
            yield _

    def get_column(self, index):
        """Return the values in a column of data."""
        return [row[index] for row in self.rows]
