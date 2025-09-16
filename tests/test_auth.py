import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_register_user(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "phone": "+71234567890",
        "password": "Password1!",
        "password_confirm": "Password1!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_register_user_password_mismatch(client: AsyncClient):
    response = await client.post("/auth/register", json={
        "full_name": "Test User",
        "email": "test2@example.com",
        "phone": "+71234567891",
        "password": "Password1!",
        "password_confirm": "Password2!"
    })
    assert response.status_code == 422


@pytest.mark.anyio
async def test_login_user(client: AsyncClient):
    # First register a user
    await client.post("/auth/register", json={
        "full_name": "Test User",
        "email": "test3@example.com",
        "phone": "+71234567892",
        "password": "Password1!",
        "password_confirm": "Password1!"
    })

    # Then login
    response = await client.post("/auth/login", json={
        "login": "test3@example.com",
        "password": "Password1!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data