import pytest


@pytest.mark.asyncio
async def test_pilot_create_flight(client, auth_headers, test_pilot):
    headers = await auth_headers(test_pilot)
    response = await client.post(
        "/api/flights/",
        json={
            "dof": "2026-03-06T03:51:31.575",
            "duration_min": 75,
            "aircraft_category": "Helicopter",
            "notes": "STD IFR TRAINING",
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json().get("status") == "Pending"
    assert response.json().get("pilot_id") == str(test_pilot.id)

@pytest.mark.asyncio
async def test_ops_create_flight(client, auth_headers, test_ops, test_pilot):
    headers = await auth_headers(test_ops)
    response = await client.post(
        "/api/flights/",
        json={
            "dof": "2026-03-06T03:51:31.575",
            "duration_min": 75,
            "aircraft_category": "Helicopter",
            "pilot_id": str(test_pilot.id),
            "notes": "STD IFR TRAINING",
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json().get("status") == "Pending"
    assert response.json().get("pilot_id") == str(test_pilot.id)
    assert response.json().get("created_by_id") == str(test_ops.id)
