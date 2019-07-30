from wootools.set_shipping_classes import (
    InternationalShipping,
    PackageTypes,
    SetShippingClasses,
    ShippingClasses,
)
from wootools.woocommerce_export import WoocommerceExport


def test_get_shipping_class():
    tests = (
        (PackageTypes.PACKET, InternationalShipping.STANDARD, ShippingClasses.STANDARD),
        (PackageTypes.PACKET, InternationalShipping.EXPRESS, ShippingClasses.HEAVY),
        (
            PackageTypes.PACKET,
            InternationalShipping.NO_INTERNATIONAL_SHIPPING,
            ShippingClasses.HEAVY,
        ),
        (
            PackageTypes.LARGE_LETTER,
            InternationalShipping.STANDARD,
            ShippingClasses.STANDARD,
        ),
        (
            PackageTypes.LARGE_LETTER,
            InternationalShipping.EXPRESS,
            ShippingClasses.HEAVY,
        ),
        (
            PackageTypes.LARGE_LETTER,
            InternationalShipping.NO_INTERNATIONAL_SHIPPING,
            ShippingClasses.HEAVY,
        ),
        (
            PackageTypes.LARGE_LETTER_SINGLE,
            InternationalShipping.STANDARD,
            ShippingClasses.STANDARD,
        ),
        (
            PackageTypes.LARGE_LETTER_SINGLE,
            InternationalShipping.EXPRESS,
            ShippingClasses.HEAVY,
        ),
        (
            PackageTypes.LARGE_LETTER_SINGLE,
            InternationalShipping.NO_INTERNATIONAL_SHIPPING,
            ShippingClasses.HEAVY,
        ),
        (
            PackageTypes.HEAVY_AND_LARGE,
            InternationalShipping.STANDARD,
            ShippingClasses.HEAVY,
        ),
        (
            PackageTypes.HEAVY_AND_LARGE,
            InternationalShipping.EXPRESS,
            ShippingClasses.HEAVY,
        ),
        (
            PackageTypes.HEAVY_AND_LARGE,
            InternationalShipping.NO_INTERNATIONAL_SHIPPING,
            ShippingClasses.HEAVY,
        ),
        (PackageTypes.COURIER, InternationalShipping.STANDARD, ShippingClasses.HEAVY),
        (PackageTypes.COURIER, InternationalShipping.EXPRESS, ShippingClasses.HEAVY),
        (
            PackageTypes.COURIER,
            InternationalShipping.NO_INTERNATIONAL_SHIPPING,
            ShippingClasses.HEAVY,
        ),
    )
    for test in tests:
        result = SetShippingClasses.get_shipping_class(test[0], test[1])
        assert result == test[2], (
            f'The Shipping Class for products with package type "{test[0]}" and '
            f'International Shipping "{test[1]}" was "{result}", expected "{test[2]}"'
        )


def test_unchanged_row():
    pid = "1"
    sku = "14M-RF0-DW3"
    woo_data = {
        WoocommerceExport.ID: pid,
        WoocommerceExport.SKU: sku,
        WoocommerceExport.SHIPPING_CLASS: ShippingClasses.HEAVY,
    }
    inv_data = {
        sku: {
            SetShippingClasses.CC_SKU_COLUMN: sku,
            SetShippingClasses.CC_RANGE_SKU_COLUMN: "RNG_EKM-PXW-S12",
            SetShippingClasses.CC_PACKAGE_TYPE_COLUMN: PackageTypes.PACKET,
            SetShippingClasses.CC_INTERNATIONAL_SHIPPING_COLUMN: InternationalShipping.EXPRESS,
        }
    }
    assert SetShippingClasses.process_export_row(woo_data, inv_data) is None


def test_changed_row():
    pid = "1"
    sku = "14M-RF0-DW3"
    woo_data = {
        WoocommerceExport.ID: pid,
        WoocommerceExport.SKU: sku,
        WoocommerceExport.SHIPPING_CLASS: ShippingClasses.STANDARD,
    }
    inv_data = {
        sku: {
            SetShippingClasses.CC_SKU_COLUMN: sku,
            SetShippingClasses.CC_RANGE_SKU_COLUMN: "RNG_EKM-PXW-S12",
            SetShippingClasses.CC_PACKAGE_TYPE_COLUMN: PackageTypes.PACKET,
            SetShippingClasses.CC_INTERNATIONAL_SHIPPING_COLUMN: InternationalShipping.EXPRESS,
        }
    }
    assert SetShippingClasses.process_export_row(woo_data, inv_data) == [
        pid,
        ShippingClasses.HEAVY,
    ]
