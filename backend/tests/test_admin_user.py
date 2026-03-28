import pytest

from app.schemas import UserRead, UserReadWithStats
from app.models import Role


@pytest.mark.asyncio
async def test_ops_can_list_users(
    client, test_ops, test_pilot, test_pilot_2, auth_headers
):
    headers = await auth_headers(test_ops)

    result = await client.get("/api/admin/users", headers=headers)

    assert result.status_code == 200


@pytest.mark.asyncio
async def test_ops_can_get_user_by_id(client, test_ops, test_pilot, auth_headers):
    headers = await auth_headers(test_ops)

    result = await client.get(f"/api/admin/users/{test_pilot.id}", headers=headers)

    assert result.status_code == 200
    assert result.json().get("id") == str(test_pilot.id)


@pytest.mark.asyncio
async def test_ops_cannot_create_user(client, test_ops, auth_headers):
    headers = await auth_headers(test_ops)

    result = await client.post(
        "/api/admin/users",
        json={"username": "new_pilot", "password": "password123", "role": Role.OPS},
        headers=headers,
    )

    assert result.status_code == 403


@pytest.mark.asyncio
async def test_ops_cannot_update_user(client, test_ops, test_pilot, auth_headers):
    headers = await auth_headers(test_ops)

    result = await client.patch(
        f"/api/admin/users/{test_pilot.id}", json={"role": Role.OPS}, headers=headers
    )

    assert result.status_code == 403


@pytest.mark.asyncio
async def test_pilot_denied_access(client, test_pilot, auth_headers):
    headers = await auth_headers(test_pilot)

    result = await client.patch(
        f"/api/admin/users/{test_pilot.id}", json={"role": Role.OPS}, headers=headers
    )

    assert result.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_request(client):
    result = await client.get("/api/admin/users")

    assert result.status_code == 401


@pytest.mark.asyncio
async def test_admin_can_create_user(client, test_admin, auth_headers):
    headers = await auth_headers(test_admin)

    result = await client.post(
        "/api/admin/users",
        json={"username": "new_pilot", "password": "password123", "role": Role.OPS},
        headers=headers,
    )

    assert result.status_code == 200


@pytest.mark.asyncio
async def test_list_users_correct_data(
    client, test_ops, test_admin, test_pilot, auth_headers
):
    headers = await auth_headers(test_ops)

    result = await client.get(
        f"/api/admin/users?active_filter=true&page=1&page_size=10", headers=headers
    )
    result = result.json()

    assert result.get("total") > 0
    assert len(result.get("items")) > 0
    assert isinstance(UserRead(**result.get("items")[0]), UserRead)

    result = await client.get(
        f"/api/admin/users?active_filter=false&page=1&page_size=10", headers=headers
    )
    result = result.json()

    assert result.get("total") == 0
    assert result.get("items") == []

    result = await client.get(
        f"/api/admin/users?role_filter=Administrator&page=1&page_size=10",
        headers=headers,
    )
    result = result.json()

    assert result.get("total") == 1
    assert isinstance(UserRead(**result.get("items")[0]), UserRead)


@pytest.mark.asyncio
async def test_ops_get_user_details(
    client, test_ops, test_pilot, pending_flight, auth_headers
):
    headers = await auth_headers(test_ops)

    result = await client.get(f"/api/admin/users/{test_pilot.id}", headers=headers)

    result = result.json()

    assert isinstance(UserReadWithStats(**result), UserReadWithStats)
    assert result.get("total_flights") > 0
    assert result.get("total_flight_hours") > 0
    assert result.get("pending_flights") > 0


@pytest.mark.asyncio
async def test_ops_get_non_existent_user_details(client, test_ops, auth_headers):
    headers = await auth_headers(test_ops)

    result = await client.get(
        "/api/admin/users/91bd6508-1c57-4807-8c6b-22613c25b164", headers=headers
    )

    assert result.status_code == 404


@pytest.mark.asyncio
async def test_ops_get_user_with_zero_details(client, test_ops, auth_headers):
    headers = await auth_headers(test_ops)

    result = await client.get(f"/api/admin/users/{test_ops.id}", headers=headers)

    result = result.json()

    assert isinstance(UserReadWithStats(**result), UserReadWithStats)
    assert result.get("total_flights") == 0
    assert result.get("total_flight_hours") == 0
    assert result.get("pending_flights") == 0


@pytest.mark.asyncio
async def test_ops_create_user_with_role(client, test_admin, auth_headers):
    headers = await auth_headers(test_admin)

    result = await client.post(
        "/api/admin/users",
        json={
            "username": "new_user_with_role",
            "password": "password123",
            "role": Role.OPS
        },
        headers=headers
    )

    assert result.status_code == 200


@pytest.mark.asyncio
async def test_duplicate_username(client, test_admin, auth_headers):
    headers = await auth_headers(test_admin)

    result = await client.post(
        "/api/admin/users",
        json={
            "username": "test_admin",
            "password": "password123",
            "role": Role.ADMIN
        },
        headers=headers
    )

    assert result.status_code == 400



@pytest.mark.asyncio
async def test_unvalid_user_create_data(client, test_admin, auth_headers):
    headers = await auth_headers(test_admin)

    result = await client.post(
        "/api/admin/users",
        json={
            "username": "ww",
            "password": "password123",
            "role": Role.PI
        },
        headers=headers
    )

    assert result.status_code == 422

    result = await client.post(
        "/api/admin/users",
        json={
            "username": "www",
            "password": "pwd",
            "role": Role.PI
        },
        headers=headers
    )

    assert result.status_code == 422


@pytest.mark.asyncio
async def test_admin_update_user(client, test_admin, test_pilot, auth_headers):
    headers = await auth_headers(test_admin)

    result = await client.patch(
        f"/api/admin/users/{test_pilot.id}",
        json={
            "username": "pilot_promoted_ops",
            "password": "newpassword123",
            "role": Role.OPS,
            "is_active": False,
        },
        headers=headers
    )

    assert result.status_code == 200

    result = result.json()

    assert result.get("username") == "pilot_promoted_ops"
    assert result.get("role") == Role.OPS
    assert result.get("is_active") == False

    attempt_login = await client.post("/api/auth/login", json={"username": "pilot_promoted_ops", "password": "newpassword123"})
    assert attempt_login.status_code == 200




@pytest.mark.asyncio
async def test_admin_updates_non_existent_user(client, test_admin, auth_headers):
    headers = await auth_headers(test_admin)

    result = await client.patch(
        "/api/admin/users/2bf92148-d56e-4e2e-b5b0-1e5d6745cf78",
        json={
            "username": "doesnt_exist",
        },
        headers=headers
    )

    assert result.status_code == 404
