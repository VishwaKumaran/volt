import pytest
from app.core.security import verify_password
from app.main import app
from app.models.user import User
from fastapi import status
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_auth_cookie_flow():
    """
    Complete test of registration and login flow:
    - register a new user
    - attempt to register again (expected failure)
    - login with wrong password (expected failure)
    - login with correct password (expected success)
    - /users/me works if cookie is set
    - /users/me failed if cookie is not set or invalid
    """

    test_user = {
        "username": "cookie_user",
        "email": "cookie_user@example.com",
        "password": "cookie_secret",
    }

    # Cleanup avant test
    await User.find_many(User.username == test_user["username"]).delete()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # --- Register user ---
        r = await ac.post("/register", json=test_user)
        assert r.status_code == status.HTTP_200_OK, r.text
        assert "set-cookie" in r.headers
        assert "access_token=" in r.headers["set-cookie"]

        user_db = await User.find_one(User.username == test_user["username"])
        assert user_db is not None
        assert verify_password(test_user["password"], user_db.hashed_password)

        # --- Register again (should fail) ---
        r2 = await ac.post("/register", json=test_user)
        assert r2.status_code == status.HTTP_400_BAD_REQUEST
        assert "already" in r2.json()["detail"].lower()

        # --- Wrong password login ---
        form_data = {
            "username": test_user["username"],
            "password": "wrongpassword",
        }
        r3 = await ac.post("/login", data=form_data)
        assert r3.status_code == status.HTTP_401_UNAUTHORIZED
        assert "bad credentials" in r3.json()["detail"].lower()

        # --- Login user ---
        form_data = {
            "username": test_user["username"],
            "password": test_user["password"],
        }
        r4 = await ac.post("/login", data=form_data)
        assert r4.status_code == status.HTTP_200_OK, r4.text
        assert "set-cookie" in r4.headers
        cookie = r4.headers["set-cookie"].split(";")[0]
        assert cookie.startswith("access_token=")

        # --- Access /users/me with cookie ---
        cookies = {"access_token": cookie.split("=", 1)[1]}
        r3 = await ac.get("/users/me", cookies=cookies)
        assert r3.status_code == status.HTTP_200_OK, r3.text
        data = r3.json()
        assert data["username"] == test_user["username"]

        # --- Access /users/me without cookie (should fail) ---
        r4 = await ac.get("/users/me")
        assert r4.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}

        # --- Access /users/me with invalid cookie (should fail) ---
        r5 = await ac.get("/users/me", cookies={"access_token": "fake_token"})
        assert r5.status_code in {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN}

    # Cleanup après test
    await User.find_many(User.username == test_user["username"]).delete()
