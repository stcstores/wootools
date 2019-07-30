"""Round prices rounds the price of products."""


from .product_update import ProductUpdate
from .woocommerce_export import WoocommerceExport


def format_price(price):
    """Return a correctly formatted price."""
    return "%.2f" % price


class RoundPrices(ProductUpdate):
    """Round prices rounds the price of products."""

    IMPORT_HEADER = [WoocommerceExport.ID, WoocommerceExport.PRICE]

    PENCE_VALUES = {25, 49, 75, 99}

    @classmethod
    def process_export_row(cls, row):
        """Return the updated price if it is changed, otherwise return None."""
        new_price = cls.fix_price(row[WoocommerceExport.PRICE])
        if new_price is not None:
            return [row[WoocommerceExport.ID], new_price]

    @classmethod
    def round_delta(cls, pence):
        """Return the number of pence to add or subtract to reach the nearest valid price."""
        prices = list(cls.PENCE_VALUES)
        prices.append(max(prices) - 100)
        rounded = min(prices, key=lambda x: abs(x - pence))
        if rounded < 0:
            delta = 0 - pence + rounded
        else:
            delta = rounded - pence
        return delta / 100

    @classmethod
    def round_price(cls, price):
        """Return a price rounded to a valid value."""
        pence = int(str(f"{price:.2f}").split(".")[1][:2])
        new_price = float(price) + cls.round_delta(pence)
        return round(new_price, 2)

    @classmethod
    def caluclate_max_price_delta(cls):
        """Return the maximum a price can change to reach a valid value."""
        gaps = [abs(cls.round_delta(i)) for i in range(100)]
        return max(gaps)

    @classmethod
    def fix_price(cls, price):
        """Return the updated price string."""
        try:
            price = float(price)
        except ValueError:
            return None
        if price < 0.01:
            return None
        if int(format_price(price).split(".")[1]) in cls.PENCE_VALUES:
            return None
        new_price = cls.round_price(price)
        cls.validate_new_price(price, new_price)
        return format_price(new_price)

    @classmethod
    def validate_new_price(cls, old_price, new_price):
        """Check a rounded price is valid and has not changed by too great an amount."""
        if new_price < 0.01:
            raise Exception("Price is less than a penny.")
        if round(abs(old_price - new_price), 2) > cls.max_price_delta:
            raise Exception(
                f"Changing price from {old_price} to {new_price} exceeds maximum of "
                f"{cls.max_price_delta}."
            )


RoundPrices.max_price_delta = RoundPrices.caluclate_max_price_delta()
