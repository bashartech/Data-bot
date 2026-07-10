from agents import Agent, RunConfig, Runner, TResponseInputItem

from ai.provider import GroqModelProvider
from ai.tools import (
    get_product_by_name,
    get_product_price,
    get_product_details,
    list_products,
    search_products,
)
from config.settings import settings

AGENT_INSTRUCTIONS = """You are an enterprise AI assistant specialized in product information. Your job is to help users find and learn about products.

You have access to product data. When a user asks about products:
1. Use the tools to look up product information
2. Provide clear, concise answers
3. If a product isn't found, suggest similar products

Available tools:
- get_product_by_name: Look up a product by its name
- get_product_price: Get the price of a specific product
- get_product_details: Get detailed specifications of a product
- list_products: List all products, optionally filtered by category
- search_products: Search for products matching a query

Be helpful and professional in your responses."""


def create_agent() -> Agent:
    return Agent(
        name="ProductAssistant",
        instructions=AGENT_INSTRUCTIONS,
        model=settings.groq_model,
        tools=[
            get_product_by_name,
            get_product_price,
            get_product_details,
            list_products,
            search_products,
        ],
    )


def _create_run_config() -> RunConfig:
    return RunConfig(
        model_provider=GroqModelProvider(),
        model_settings=None,
        tracing_disabled=True,
    )


async def run_agent(
    input: str | list[TResponseInputItem],
    context: object | None = None,
    max_turns: int = 10,
) -> str:
    agent = create_agent()
    run_config = _create_run_config()
    result = await Runner.run(
        starting_agent=agent,
        input=input,
        context=context,
        max_turns=max_turns,
        run_config=run_config,
    )
    return result.final_output


async def run_agent_streamed(
    input: str | list[TResponseInputItem],
    context: object | None = None,
    max_turns: int = 10,
):
    agent = create_agent()
    run_config = _create_run_config()
    result = Runner.run_streamed(
        starting_agent=agent,
        input=input,
        context=context,
        max_turns=max_turns,
        run_config=run_config,
    )
    return result
