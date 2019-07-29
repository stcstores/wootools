"""Round prices rounds the price of products."""

import csv
import sys

import click

from .woocommerce_export import WoocommerceExport


class RoundPrices:
    """Round prices rounds the price of products."""

    SKU_COLUMN = "VAR_SKU"
    RANGE_SKU_COLUMN = "RNG_SKU"
    PRICE_COLUMN = "VAR_Price_Net"

    OUTPUT_HEADER = [WoocommerceExport.ID, WoocommerceExport.PRICE]

    PENCE_VALUES = [25, 49, 75, 99]

    def __init__(self, woo_export_path):
        """Calculate rounded prices and write a csv to make the changes to stdout."""
        self.WC_export = WoocommerceExport(woo_export_path)
        self.max_price_delta = self.caluclate_max_price_delta()
        output_data = self.output_data()
        exit()
        self.write_status(output_data)
        self.write_output(output_data)

    def round_delta(self, pence):
        """Return the number of pence to add or subtract to reach the nearest valid price."""
        prices = self.PENCE_VALUES
        prices.append(max(prices) - 100)
        rounded = min(self.PENCE_VALUES, key=lambda x: abs(x - pence))
        if rounded < 0:
            delta = 0 - pence + rounded
        else:
            delta = rounded - pence
        return delta / 100

    def round_price(self, price):
        """Return a price rounded to a valid value."""
        pence = int(str(f"{price:.2f}").split(".")[1][:2])
        new_price = float(price) + self.round_delta(pence)
        return round(new_price, 2)

    def caluclate_max_price_delta(self):
        """Return the maximum a price can change to reach a valid value."""
        gaps = [abs(self.round_delta(i)) for i in range(100)]
        return max(gaps)

    def write_status(self, output_data):
        """Write completeion message to stderr."""
        click.echo(f"{len(output_data)} update rows.", err=True)

    def output_data(self):
        """Return the CSV data as a list of rows."""
        data = []
        for row in self.WC_export:
            new_price = self.fix_price(row[self.WC_export.PRICE])
            if new_price is not None:
                data.append([row[self.WC_export.ID], new_price])
        return data

    def fix_price(self, price):
        """Return the updated price string."""
        try:
            price = float(price)
        except ValueError:
            return None
        if price < 0.01:
            return None
        price = float(price)
        new_price = self.round_price(price)
        self.validate_new_price(price, new_price)
        return str(new_price)

    def validate_new_price(self, old_price, new_price):
        """Check a rounded price is valid and has not changed by too great an amount."""
        if new_price < 0.01:
            raise Exception("Price is less than a penny.")
        if round(abs(old_price - new_price), 2) > self.max_price_delta:
            raise Exception(
                f"Changing price from {old_price} to {new_price} exceeds maximum of "
                f"{self.max_price_delta}."
            )

    def write_output(self, output_data):
        """Write update CSV to stdout."""
        f = csv.writer(sys.stdout)
        f.writerow(self.OUTPUT_HEADER)
        f.writerows(output_data)
