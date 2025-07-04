# Shopify Checkout Automation

A simple checkout agent written in Python using the [Browser Use](https://github.com/browser-use/browser-use) library.

A Python-based automation tool that uses browser automation to complete Shopify store checkouts programmatically.

## Usage

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd shopify-checkout
    ```

2. [Install `uv`](https://github.com/astral-sh/uv?tab=readme-ov-file#installation) if you don't already have it installed.

3. Install dependencies:
    ```bash
    uv init
    uv pip install -r requirements.txt
    ```

4. Set up environment variables:
    ```bash
    cp .env.example .env
    # Edit .env with your OpenAI API key
    ```

5. Run it!
    ```bash
    uv run agent.py
    ```

## Customization

Edit the `main()` function in `agent.py` with your order details:

```python
request = Request(
    first_name="Your Name",
    last_name="Your Last Name",
    email_address="your.email@example.com",
    shipping_address="123 Main St, City, Country 12345",

    # Payment details (use test card for development)
    card_number="4242424242424242",
    card_expiry_month="12",
    card_expiry_year="25",
    card_cvv="123",

    store_password="your_store_password",  # Leave empty if no password
    product_urls=["https://your-store.myshopify.com/products/product-name"]
)
```

## Disclaimer

This tool is for educational and development purposes. Always comply with Shopify's terms of service and applicable laws when using automation tools.
