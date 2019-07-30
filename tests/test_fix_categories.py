from wootools.fix_categories import FixCategories
from wootools.woocommerce_export import WoocommerceExport


def test_add_uncategorized():
    categories = FixCategories.update_categories([])
    assert categories == [FixCategories.UNCATEGORIZED]


def test_remove_uncategorized():
    categories = FixCategories.update_categories(
        [FixCategories.UNCATEGORIZED, "Clothes"]
    )
    assert categories == ["Clothes"]


def test_unchanged_categories():
    categories = FixCategories.update_categories(["Clothes"])
    assert categories is None


def test_export_row_with_no_changes():
    pid = "1"
    row = {WoocommerceExport.ID: pid, WoocommerceExport.CATEGORIES: "Clothes, Home"}
    assert FixCategories.process_export_row(row) is None


def test_export_row_adding_uncategorized():
    pid = "1"
    row = {WoocommerceExport.ID: pid, WoocommerceExport.CATEGORIES: ""}
    assert FixCategories.process_export_row(row) == [pid, FixCategories.UNCATEGORIZED]


def test_export_row_removing_uncategorized():
    pid = "1"
    row = {
        WoocommerceExport.ID: pid,
        WoocommerceExport.CATEGORIES: f"Clothes, {FixCategories.UNCATEGORIZED}, Home",
    }
    assert FixCategories.process_export_row(row) == [pid, "Clothes, Home"]
