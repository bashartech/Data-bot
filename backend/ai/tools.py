from agents import RunContextWrapper, function_tool

from config.logging import logger
from repositories.product_repo import ProductRepository


@function_tool
async def get_product_by_name(
    context: RunContextWrapper,
    name: str,
) -> str:
    repo = ProductRepository(context.context.session)
    product = await repo.get_by_name(name)
    if product is None:
        return f"No product found with name '{name}'"
    return _format_product(product)


@function_tool
async def get_product_price(
    context: RunContextWrapper,
    name: str,
) -> str:
    repo = ProductRepository(context.context.session)
    product = await repo.get_by_name(name)
    if product is None:
        return f"No product found with name '{name}'"
    return f"{product.product_name} costs ${product.price:.2f}"


@function_tool
async def get_product_details(
    context: RunContextWrapper,
    name: str,
) -> str:
    repo = ProductRepository(context.context.session)
    product = await repo.get_by_name(name)
    if product is None:
        return f"No product found with name '{name}'"
    if not product.detail:
        return f"No details available for '{product.product_name}'"
    return (
        f"Product: {product.product_name}\n"
        f"Category: {product.category}\n"
        f"Description: {product.description}\n"
        f"Price: ${product.price:.2f}\n"
        f"Stock: {product.stock}\n"
        f"Manufacturer: {product.manufacturer}\n"
        f"Specifications: {product.detail.specifications}\n"
        f"Warranty: {product.detail.warranty}\n"
        f"Country: {product.detail.country}\n"
        f"Weight: {product.detail.weight} kg"
    )


@function_tool
async def list_products(
    context: RunContextWrapper,
    category: str | None = None,
) -> str:
    repo = ProductRepository(context.context.session)
    products = await repo.list_all(limit=50)
    if not products:
        return "No products available"

    if category:
        products = [p for p in products if p.category.lower() == category.lower()]

    lines = ["Available products:"]
    for p in products:
        lines.append(f"- {p.product_name} (${p.price:.2f}) - {p.category}")
    return "\n".join(lines)


@function_tool
async def search_products(
    context: RunContextWrapper,
    query: str,
) -> str:
    repo = ProductRepository(context.context.session)
    products = await repo.search(query)
    if not products:
        return f"No products found matching '{query}'"
    lines = [f"Products matching '{query}':"]
    for p in products:
        lines.append(f"- {p.product_name} (${p.price:.2f}) - {p.category}")
    return "\n".join(lines)


def _format_product(product) -> str:
    return (
        f"Product: {product.product_name}\n"
        f"Category: {product.category}\n"
        f"Description: {product.description}\n"
        f"Price: ${product.price:.2f}\n"
        f"Stock: {product.stock}\n"
        f"Manufacturer: {product.manufacturer}"
    )
