import httpx, os

AMAZON_URL = os.getenv("AMAZON_API_URL")
AMAZON_KEY = os.getenv("AMAZON_ACCESS_KEY")
AMAZON_SECRET = os.getenv("AMAZON_SECRET_KEY")

# Placeholders -- real SP-API requires AWS sigv4, etc., for demo only
def amazon_headers():
    return {"x-access-key": AMAZON_KEY, "x-secret-key": AMAZON_SECRET, "Content-Type":"application/json"}

async def amazon_export_product(product):
    payload = {
        "productType": "footwear",
        "name": product['name'],
        "category": product.get("category", "Footwear"),
        "variation": {"size": product.get("size"), "color": product.get("color")},
        "price": product.get("price"),
        "quantity": product.get("stock"),
        "sku": product.get("_id")
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{AMAZON_URL}/products", json=payload, headers=amazon_headers())
        return r.json()

async def amazon_update_stock(product_id, stock):
    payload = {"quantity": stock}
    async with httpx.AsyncClient() as client:
        r = await client.put(f"{AMAZON_URL}/products/{product_id}/inventory", json=payload, headers=amazon_headers())
        return r.json()
