import os
import pytest
from fastapi.testclient import TestClient
from main import app
import database

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown(tmp_path):
    # Create a temporary hello.html file for testing
    html_file = tmp_path / "hello.html"
    html_file.write_text("<html><body>Hello Test</body></html>")
    # Change working dir so FileResponse can find the file
    cwd = os.getcwd()
    os.chdir(tmp_path)
    # Reset sample_products before each test
    database.sample_products[:] = [
        database.sample_product_1,
        database.sample_product_2,
        database.sample_product_3,
        database.sample_product_4,
        database.sample_product_5,
    ]
    yield
    # Teardown: revert cwd
    os.chdir(cwd)

# get 1
def test_read_root_success():
    response = client.get("/hello")
    assert response.status_code == 200
    assert b"Hello Test" in response.content


# get 2
def test_get_products_success():
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 5

def test_get_products_not_found():
    response = client.get("/productss")  # wrong path
    assert response.status_code == 404

# get + param
def test_get_product_success():
    pid = database.sample_product_3["product_id"]
    response = client.get(f"/product/{pid}")
    assert response.status_code == 200
    assert response.json()["product_id"] == pid

def test_get_product_not_found_error():
    response = client.get("/product/9999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"

# post
def test_create_product_success():
    new_product = {"product_id": 999, "name": "TestProd", "category": "Test", "price": 1.23}
    response = client.post("/product", json=new_product)
    assert response.status_code == 201
    assert response.json() == new_product


def test_create_product_duplicate_error():
    existing = database.sample_product_1.copy()
    response = client.post("/product", json=existing)
    assert response.status_code == 400
    assert response.json()["detail"] == "Item with this ID already exists"

# delete
def test_delete_product_success():
    pid = database.sample_product_2["product_id"]
    response = client.delete(f"/product/{pid}")
    assert response.status_code == 204
    get_resp = client.get(f"/product/{pid}")
    assert get_resp.status_code == 404

def test_delete_product_not_found_error():
    response = client.delete("/product/5555")
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"