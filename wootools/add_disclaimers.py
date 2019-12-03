"""AddDisclaimers adds disclaimers to the descriptions of products in the knives category."""

from .product_update import ProductUpdate
from .woocommerce_export import WoocommerceExport


class AddDisclaimers(ProductUpdate):
    """AddDisclaimers adds disclaimers to the descriptions of products in the knives category."""

    IMPORT_HEADER = [WoocommerceExport.ID, WoocommerceExport.DESCRIPTION]

    disclaimer_categories = ["Knives"]
    html_class = "disclaimer"
    disclaimer = "\\n".join(
        [
            "\\n<br>",
            f"<div class='{html_class}'>",
            "\t<p>DISCLAIMER:</p>",
            "\t<p>You must be 18 years or older in order to purchase this product.</p>",
            (
                "\t<p>ID will be required on delivery to the UK. The product will not "
                "be delivered to anyone under the age of 18 or without valid proof of "
                "age. The buyer is responsible for any additional shipping charge "
                "incurred if ID is not available.</p>"
            ),
            (
                "\t<p>It is the buyers obligation that they ensure they know their states "
                "rules and regulation in regards to knives and to make sure they are "
                "not breaking the law by purchasing knives.</p>"
            ),
            (
                "\t<p>By purchasing from this website and you agree that you are 18 years "
                "or older and understand rules and regulations in relation to knives in "
                "your own state or territory.</p>"
            ),
            "</div>",
        ]
    )

    @classmethod
    def process_export_row(cls, row):
        """Return an update row if an update is required, otherwise return None."""
        if any(
            _ in row[WoocommerceExport.CATEGORIES] for _ in cls.disclaimer_categories
        ):
            description = cls.add_disclaimer(row[WoocommerceExport.DESCRIPTION])
            if description is not None:
                return [row[WoocommerceExport.ID], description]
        return None

    @classmethod
    def add_disclaimer(cls, description):
        """Add the disclaimer to a description."""
        if f"<div class='{cls.html_class}'>" not in description:
            updated_description = description.replace("\n", "\\n") + cls.disclaimer
            return updated_description
        return None
