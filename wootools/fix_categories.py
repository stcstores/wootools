"""
FixCategories updates category information.

It removes the Uncategorized category from products with any other category and
adds Uncategorized to any products with no category.
"""


from .product_update import ProductUpdate
from .woocommerce_export import WoocommerceExport


class FixCategories(ProductUpdate):
    """
    FixCategories updates category information.

    It removes the Uncategorized category from products with any other category and
    adds Uncategorized to any products with no category.
    """

    UNCATEGORIZED = "Uncategorized"
    IMPORT_HEADER = [WoocommerceExport.ID, WoocommerceExport.CATEGORIES]

    @classmethod
    def process_export_row(cls, row):
        """Return an  updated CSV row if updates are necessary, otherwise return None."""
        current_categories = cls.parse_categories(row[WoocommerceExport.CATEGORIES])
        non_empty_categories = cls.add_uncategorized(current_categories)
        fixed_categories = cls.remove_uncategorized(non_empty_categories)
        if fixed_categories != current_categories:
            return [row[WoocommerceExport.ID], cls.format_categories(fixed_categories)]
        return None

    @classmethod
    def add_uncategorized(cls, categories):
        """Add Uncategorized to categories if it is an empty list."""
        if len(categories) == 0:
            categories = [cls.UNCATEGORIZED]
        return categories

    @classmethod
    def remove_uncategorized(cls, categories):
        """Remove Uncategroized from categories if it contains other categories."""
        if cls.UNCATEGORIZED in categories and len(categories) > 1:
            categories = [_ for _ in categories if _ != cls.UNCATEGORIZED]
        return categories

    @staticmethod
    def parse_categories(category_column_contents):
        """Return an export categories field as a list of categories."""
        return [_.strip() for _ in category_column_contents.split(",")]

    @staticmethod
    def format_categories(categories):
        """Return a list of categories formatted for a Woocommerce CSV file."""
        return ", ".join(categories)
