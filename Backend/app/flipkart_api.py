import httpx, os

FLIPKART_URL = os.getenv("FLIPKART_API_URL")
FLIPKART_TOKEN = os.getenv("FLIPKART_ACCESS_TOKEN")

async def flipkart_export_product(product):
    headers = {"Authorization": f"Bearer {FLIPKART_TOKEN}", "Content-Type": "application/json"}
    product_payload = {
        "listing": {
            "product_name": product['name'],
            "brand": product.get("category", "Footwear"),
            "size": product.get("size"),
            "color": product.get("color"),
            "price": product.get("price"),
            "stock": product.get("stock")
        }
        # Add other required fields per flipkart API docs
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{FLIPKART_URL}/listings", json=product_payload, headers=headers)
        return r.json()

async def flipkart_update_stock(product_id, stock):
    headers = {"Authorization": f"Bearer {FLIPKART_TOKEN}", "Content-Type": "application/json"}
    update_payload = {"stock": stock}
    async with httpx.AsyncClient() as client:
        r = await client.put(f"{FLIPKART_URL}/listings/{product_id}/stock", json=update_payload, headers=headers)
        return r.json()
