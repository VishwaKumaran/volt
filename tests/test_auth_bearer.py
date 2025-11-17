import uuid

import pytest
import pytest_asyncio
from app.core.security import verify_password
from app.main import app
from app.models.user import User
from asgi_lifespan import LifespanManager
from fastapi import status
from httpx import AsyncClient, ASGITransport
from tests_utils.db_utils import delete_user, find_user


@pytest_asyncio.fixture
async def client():
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac


@pytest.mark.asyncio
async def test_register_and_login_flow(client):
    """
    Complete test of registration and login flow:
    - register a new user
    - attempt to register again (expected failure)
    - login with wrong password (expected failure)
    - login with correct password (expected success)
    - /users/me works if bearer token is set
    - /users/me failed if bearer token is not set or invalid
    """
    test_user = {
        "username": uuid.uuid4().hex,
        "email": f"{uuid.uuid4().hex}@example.com",
        "password": "secret123",
    }

    # Cleanup before test
    # await delete_user(User, test_user["username"])

    # --- Register ---
    r = await client.post("/register", json=test_user)
    assert r.status_code == status.HTTP_200_OK, r.text
    data = r.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Check if the user is created
    user_db = await find_user(User, test_user["username"])
    assert user_db is not None
    assert verify_password(test_user["password"], user_db.hashed_password)

    # --- Register again (should fail) ---
    r2 = await client.post("/register", json=test_user)
    assert r2.status_code == status.HTTP_400_BAD_REQUEST
    assert "already" in r2.json()["detail"].lower()

    # --- Wrong password login ---
    form_data = {
        "username": test_user["username"],
        "password": "wrongpassword",
    }
    r3 = await client.post("/login", data=form_data)
    assert r3.status_code == status.HTTP_401_UNAUTHORIZED
    assert "bad credentials" in r3.json()["detail"].lower()

    # --- Correct login ---
    form_data["password"] = test_user["password"]
    r4 = await client.post("/login", data=form_data)
    assert r4.status_code == status.HTTP_200_OK
    login_token = r4.json()
    assert "access_token" in login_token
    assert login_token["token_type"] == "bearer"

    # --- Access /users/me with valid token ---
    print("QSDFJQSIFDHZAIOFNHAZ", login_token)
    headers = {"Authorization": f"Bearer {login_token['access_token']}"}
    r3 = await client.get("/users/me", headers=headers)
    assert r3.status_code == status.HTTP_200_OK, r3.text
    data = r3.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]

    # --- Access /users/me with invalid token ---
    bad_headers = {"Authorization": "Bearer invalidtoken"}
    r4 = await client.get("/users/me", headers=bad_headers)
    assert r4.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}

    # Cleanup after test
    await delete_user(User, test_user["username"])
