import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_add_to_cart_unauthorized(client: AsyncClient):
    response = await client.post("/cart/add", json={
        "product_id": 1,
        "quantity": 2
    })
    assert response.status_code == 401

@pytest.mark.anyio
async def test_get_cart_unauthorized(client: AsyncClient):
    response = await client.get("/cart/items")
    assert response.status_code == 401