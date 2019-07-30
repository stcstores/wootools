from wootools.round_prices import RoundPrices
from wootools.woocommerce_export import WoocommerceExport


def test_round_price():
    prices = [round(i / 100, 2) for i in range(1, 15001)]
    for price in prices:
        new_price = RoundPrices.round_price(price)
        assert new_price >= RoundPrices.MIN_PRICE
        assert new_price >= price - RoundPrices.max_price_delta
        assert (
            new_price == RoundPrices.MIN_PRICE
            or new_price <= price + RoundPrices.max_price_delta
        )
        price_pence = int(RoundPrices.format_price(new_price).split(".")[1])
        assert price_pence in RoundPrices.PENCE_VALUES


def test_unchanged_row():
    pid = "1"
    row = {
        WoocommerceExport.ID: pid,
        WoocommerceExport.PRICE: RoundPrices.fix_price(15.63),
    }
    assert RoundPrices.process_export_row(row) is None


def test_changed_row():
    pid = "1"
    row = {WoocommerceExport.ID: pid, WoocommerceExport.PRICE: "0.01"}
    assert RoundPrices.process_export_row(row) == [
        pid,
        RoundPrices.format_price(RoundPrices.MIN_PRICE),
    ]


def test_prices():
    assert RoundPrices.fix_price("0.01") == "0.25"
    assert RoundPrices.fix_price("0.10") == "0.25"
    assert RoundPrices.fix_price("0.25") is None
    assert RoundPrices.fix_price("0.37") == "0.25"
    assert RoundPrices.fix_price("0.38") == "0.49"
    assert RoundPrices.fix_price("0.49") is None
    assert RoundPrices.fix_price("0.75") is None
    assert RoundPrices.fix_price("0.97") == "0.99"
    assert RoundPrices.fix_price("0.99") is None
    assert RoundPrices.fix_price("1.00") == "0.99"
    assert RoundPrices.fix_price("1.25") is None
    assert RoundPrices.fix_price("1.96") == "1.99"
    assert RoundPrices.fix_price("2.00") == "1.99"
    assert RoundPrices.fix_price("2.80") == "2.75"
    assert RoundPrices.fix_price("1052.92") == "1052.99"
