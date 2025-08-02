from fastapi import FastAPI, Depends, HTTPException, status
from app.models import *
from app.database import product_collection, sale_collection, user_collection
from app.auth import *
from app.flipkart_api import flipkart_export_product, flipkart_update_stock
from app.amazon_api import amazon_export_product, amazon_update_stock
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.post("/register")
async def register(user: User):
    existing = await user_collection.find_one({"username": user.username})
    if existing:
        raise HTTPException(409, "Username exists")
    hashed = get_password_hash(user.password)
    user.password = hashed
    await user_collection.insert_one(user.dict())
    return {"status":"ok"}

@app.post("/token")
async def login(user: UserLogin):
    auth = await authenticate_user(user.username, user.password)
    if not auth:
        raise HTTPException(401, "Invalid login")
    token = create_access_token({"sub": user.username, "role": auth["role"]})
    return {"access_token": token, "token_type": "bearer", "role": auth["role"]}

@app.get("/me")
async def me(user=Depends(get_current_user)):
    return {"user":user["username"], "role": user["role"]}

# ==== PRODUCTS ====
@app.post("/products", dependencies=[Depends(get_user_role(['admin','inventory']))])
async def add_product(product: Product):
    prod = await product_collection.insert_one(product.dict())
    return {"id": str(prod.inserted_id)}

@app.get("/products")
async def list_products(user=Depends(get_current_user)):
    data = [ {**p, "_id": str(p["_id"])} async for p in product_collection.find()]
    return data

@app.put("/products/{pid}")
async def update_product(pid: str, product: Product, user=Depends(get_user_role(['admin','inventory']))):
    prod = await product_collection.find_one({"_id": ObjectId(pid)})
    if not prod:
        raise HTTPException(404, detail="Product not found")
    await product_collection.update_one({"_id": ObjectId(pid)}, {"$set": product.dict()})
    return {"status": "updated"}

# ==== SALES ====
@app.post("/sales", dependencies=[Depends(get_user_role(['admin','sales']))])
async def record_sale(sale: Sale):
    total = 0.0
    update_bulk = []
    items = []
    for item in sale.items:
        prod = await product_collection.find_one({"_id": ObjectId(item.product_id)})
        if not prod or prod["stock"] < item.quantity:
            raise HTTPException(400, f"Insufficient stock for {prod['name'] if prod else item.product_id}")
        update_bulk.append({
            "filter": {"_id": ObjectId(item.product_id)},
            "update": {"$inc": {"stock": -item.quantity}}
        })
        total += prod['price'] * item.quantity
        items.append({"product_id": item.product_id, "qty": item.quantity, "name": prod['name']})

    # Atomically update stock
    for upd in update_bulk:
        await product_collection.update_one(upd["filter"], upd["update"])

    sale_id = (await sale_collection.insert_one({"items": items, "customer": sale.customer, "total": total})).inserted_id

    # Update stock on marketplaces
    for item in sale.items:
        prod = await product_collection.find_one({"_id": ObjectId(item.product_id)})
        # Flipkart
        await flipkart_update_stock(item.product_id, prod['stock'])
        # Amazon
        await amazon_update_stock(item.product_id, prod['stock'])

    return {"id": str(sale_id), "total": total}

# ==== BILLING ====
@app.get("/billing/{sale_id}", dependencies=[Depends(get_user_role(['admin','billing']))])
async def generate_bill(sale_id: str):
    sale = await sale_collection.find_one({"_id": ObjectId(sale_id)})
    if not sale:
        raise HTTPException(404, detail="Sale not found")
    gst = 0.18 * sale["total"]
    return {
        "customer": sale.get("customer"),
        "total": sale["total"],
        "GST": gst,
        "total_payable": sale["total"] + gst
    }

# ==== MARKETPLACE EXPORT ====
@app.post("/export/flipkart/{pid}", dependencies=[Depends(get_user_role(['admin']))])
async def export_to_flipkart(pid: str):
    prod = await product_collection.find_one({"_id": ObjectId(pid)})
    if not prod:
        raise HTTPException(404, detail="Product not found")
    result = await flipkart_export_product(prod)
    return ExportResponse(status="ok", detail=f"Flipkart response: {result}")

@app.post("/export/amazon/{pid}", dependencies=[Depends(get_user_role(['admin']))])
async def export_to_amazon(pid: str):
    prod = await product_collection.find_one({"_id": ObjectId(pid)})
    if not prod:
        raise HTTPException(404, detail="Product not found")
    result = await amazon_export_product(prod)
    return ExportResponse(status="ok", detail=f"Amazon response: {result}")
