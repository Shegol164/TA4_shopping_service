import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_get_products_unauthorized(client: AsyncClient):
    response = await client.get("/products/")
    assert response.status_code == 401

@pytest.mark.anyio
async def test_create_product_unauthorized(client: AsyncClient):
    response = await client.post("/products/", json={
        "name": "Test Product",
        "price": "99.99"
    })
    assert response.status_code == 401