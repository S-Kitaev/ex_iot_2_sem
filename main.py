from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn
from database import sample_products

app = FastAPI()

@app.get("/hello")
def read_root():
    return FileResponse("hello.html")

@app.get("/products")
def get_items():
    return sample_products

@app.get("/product/{product_id}")
def get_item(product_id: int):
    for product in sample_products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/product", status_code=201)
def create_item(product: dict):
    if any(i["product_id"] == product["product_id"] for i in product):
        raise HTTPException(status_code=400, detail="Item with this ID already exists")
    sample_products.append(product)
    return product

@app.delete("/product/{product_id}", status_code=204)
def delete_item(product_id: int):
    for idx, product in enumerate(sample_products):
        if product["product_id"] == product_id:
            sample_products.pop(idx)
            return
    raise HTTPException(status_code=404, detail="Product not found")

if __name__ == '__main__':
    uvicorn.run(app,
                host='127.0.0.1',
                port=80)