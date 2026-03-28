import pytest


@pytest.mark.asyncio
async def test_ops_access_statistics(client, auth_headers, test_ops):
    headers = await auth_headers(test_ops)
    stats = await client.get("/api/admin/statistics", headers=headers)
    assert stats.status_code == 200


@pytest.mark.asyncio
async def test_admin_access_statistics(client, auth_headers, test_admin):
    headers = await auth_headers(test_admin)
    stats = await client.get("/api/admin/statistics", headers=headers)
    assert stats.status_code == 200


@pytest.mark.asyncio
async def test_unauthorized_access_statistics(client, auth_headers, test_pilot):
    headers = await auth_headers(test_pilot)
    stats = await client.get("/api/admin/statistics", headers=headers)
    assert stats.status_code == 403

    stats = await client.get("/api/admin/statistics")
    assert stats.status_code == 401


@pytest.mark.asyncio
async def test_correct_statistics(
    client,
    auth_headers,
    test_ops,
    approved_flight,
    pending_flight_pilot_2,
    test_pilot,
    test_pilot_2,
):
    headers = await auth_headers(test_ops)
    stats = await client.get("/api/admin/statistics", headers=headers)

    assert stats.status_code == 200
    assert stats.json().get("total_flights") == 2

    assert stats.json().get("pending_flights") == 1
    assert stats.json().get("approved_flights") == 1

    assert stats.json().get("flights_by_aircraft_category") == {
        "Helicopter": 2,
        "Fixed-wing": 0,
        "Glider": 0,
    }

    assert stats.json().get("flights_by_pilot") == {
        test_pilot.username: 1,
        test_pilot_2.username: 1,
    }

    assert stats.json().get("total_hours") == 3


@pytest.mark.asyncio
async def test_empty_db_returns_zeros(
    client, auth_headers, test_ops, test_pilot, test_pilot_2
):
    headers = await auth_headers(test_ops)
    stats = await client.get("/api/admin/statistics", headers=headers)

    assert stats.status_code == 200
    assert stats.json().get("total_flights") == 0

    assert stats.json().get("flights_by_aircraft_category") == {
        "Helicopter": 0,
        "Fixed-wing": 0,
        "Glider": 0,
    }

    assert stats.json().get("flights_by_pilot") == {}

    assert stats.json().get("total_hours") == 0
