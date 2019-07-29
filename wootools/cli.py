"""Wootools CLI applications."""

import click

from .add_disclaimers import AddDisclaimers
from .fix_categories import FixCategories
from .round_prices import RoundPrices
from .set_shipping_classes import SetShippingClasses

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.pass_context
def cli(ctx):
    """Run subcommands."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.pass_context
@click.argument(
    "export_file_path",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
)
def fix_categories(ctx, export_file_path):
    """
    Update Woocommerce product categories.

    Takes a current Product Export from a woocommerce site and writes an import file to
    STDOUT that will update all the product's categories such that:

    - All products are in a category (Adds the "Uncategorized" category to products
    without a category).

    - Removes the "Uncategorized" category from products with other categories set.
    """
    FixCategories(export_file_path)


@cli.command()
@click.pass_context
@click.option(
    "-w",
    "--woo_export_path",
    "woo_export_path",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    required=True,
)
@click.option(
    "-i",
    "--cc_export_path",
    "cc_export_path",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
    required=True,
)
def set_shipping_classes(ctx, woo_export_path, cc_export_path):
    """
    Set shipping classes for Woocommerce products.

    Sets the correct shipping classes for products acording to their "Package Type" and
    "International Shipping" settings in Cloud Commerce.
    """
    SetShippingClasses(woo_export_path=woo_export_path, cc_export_path=cc_export_path)


@cli.command()
@click.pass_context
@click.argument(
    "export_file_path",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
)
def add_disclaimers(ctx, export_file_path):
    """
    Add age disclaimers to products in the Knives category.

    Writes an import file to STDOUT that will update add the disclaimer to products with
    the Knives category.
    """
    AddDisclaimers(export_file_path)


@cli.command()
@click.pass_context
@click.argument(
    "export_file_path",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True
    ),
)
def round_prices(ctx, export_file_path):
    """
    Round product prices.

    Takes a current Product Export from a woocommerce site and writes an import file to
    STDOUT that will round all product prices such that the end with .25, .49, .75. .99.
    """
    RoundPrices(export_file_path)
