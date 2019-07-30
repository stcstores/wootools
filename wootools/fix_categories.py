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
        categories = cls.parse_categories(row[WoocommerceExport.CATEGORIES])
        fixed_categories = cls.update_categories(categories)
        if fixed_categories is not None:
            return [row[WoocommerceExport.ID], cls.format_categories(fixed_categories)]

    @classmethod
    def update_categories(cls, categories):
        """Return an updated category list."""
        if categories == []:
            return [cls.UNCATEGORIZED]
        if cls.UNCATEGORIZED in categories:
            return [_ for _ in categories if _ != cls.UNCATEGORIZED]

    @staticmethod
    def parse_categories(category_column_contents):
        """Return an export categories field as a list of categories."""
        return [_.strip() for _ in category_column_contents.split(",") if _]

    @staticmethod
    def format_categories(categories):
        """Return a list of categories formatted for a Woocommerce CSV file."""
        return ", ".join(categories)
