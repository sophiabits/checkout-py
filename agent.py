from langchain_openai import ChatOpenAI
from browser_use import Agent, BrowserSession, Controller
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

import asyncio

llm = ChatOpenAI(model="gpt-4o")


class Request(BaseModel):
    first_name: str
    last_name: str
    email_address: str
    shipping_address: str

    card_number: str
    card_expiry_month: str
    card_expiry_year: str
    card_cvv: str

    store_password: str
    product_urls: list[str]


class OrderItem(BaseModel):
    title: str
    quantity: int
    price: float


class Order(BaseModel):
    id: str
    items: list[OrderItem]
    url: str

    currency_code: str
    shipping: float
    subtotal: float
    tax: float
    total: float


class Checkout(BaseModel):
    url: str

    currency_code: str
    """Total price of the checkout, including shipping, tax, etc."""
    total_price: float


async def prepare_checkout(session: BrowserSession, request: Request):
    product_urls_list = "\n".join([f"* {url}" for url in request.product_urls])

    task = f"""
Open the checkout page for an order containing the following products:
{product_urls_list}

Add products to the cart by directly navigating to each product URL.

The password for the store is "{request.store_password}"

Shipping address: {request.shipping_address}

Enter the shipping address so that shipping methods are available.

Then return the final details of the checkout page alongside its URL.
""".strip()

    controller = Controller(output_model=Checkout)

    agent = Agent(
        browser_session=session,
        controller=controller,
        llm=llm,
        task=task,
    )
    history = await agent.run()

    result = history.final_result()
    parsed = Checkout.model_validate_json(result)
    return parsed


async def do_checkout(session: BrowserSession, request: Request, checkout: Checkout):
    task = f"""
Complete checkout for the following checkout page: {checkout.url}

The password for the store is "{request.store_password}"

Customer details:
* Email: {request.email_address}
* First name: {request.first_name}
* Last name: {request.last_name}

Shipping address:

Payment details:
* Number: x_card_number
* Expiry: x_card_expiry_month / x_card_expiry_year
* CVV: x_card_cvv
* Name on card: {request.first_name} {request.last_name}

Do not tick "remember me".

After checkout, return the details of the order.
""".strip()

    controller = Controller(output_model=Order)
    agent = Agent(
        browser_session=session,
        controller=controller,
        llm=llm,
        task=task,
        sensitive_data={
            "https://sophiabits-dev.myshopify.com": {
                "x_card_number": request.card_number,
                "x_card_expiry_month": request.card_expiry_month,
                "x_card_expiry_year": request.card_expiry_year,
                "x_card_cvv": request.card_cvv,
            },
        },
        # Must turn off vision to avoid leaking sensitive data through screenshots
        use_vision=False,
    )
    history = await agent.run()

    result = history.final_result()
    return Order.model_validate_json(result)


async def main():
    request = Request(
        # Fill in with your own values
        first_name="Sophia",
        last_name="Willows",
        email_address="hello@sophiabits.com",
        shipping_address="123 Main St, Huntly, Waikato, New Zealand 3700",
        # Test mode Shopify card number
        card_number="1",
        card_expiry_month="02",
        card_expiry_year="26",
        card_cvv="123",
        store_password="girtoh",
        product_urls=["https://sophiabits-dev.myshopify.com/products/example-shirt"],
    )

    session = BrowserSession(
        allowed_domains=["https://sophiabits-dev.myshopify.com"],
        keep_alive=True,
        stealth=True,
        storage_state={},
        user_data_dir=None,
    )
    await session.start()

    checkout = await prepare_checkout(session, request)
    order = await do_checkout(session, request, checkout)
    print(order.model_dump_json(indent=2))

    await session.kill()


asyncio.run(main())
