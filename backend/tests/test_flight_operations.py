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


@pytest.mark.asyncio
async def test_ops_approve_flight(client, auth_headers, test_ops, pending_flight):
    headers = await auth_headers(test_ops)
    approved = await client.post(
        f"/api/flights/{pending_flight.get('id')}/approve",
        json={},
        headers=headers,
    )
    assert approved.status_code == 200
    assert approved.json().get("status") == "Approved"


@pytest.mark.asyncio
async def test_pilot_approve_flight(client, auth_headers, test_pilot, pending_flight):
    headers = await auth_headers(test_pilot)
    approved = await client.post(
        f"/api/flights/{pending_flight.get('id')}/approve",
        json={},
        headers=headers,
    )
    assert approved.status_code == 403


@pytest.mark.asyncio
async def test_ops_approve_already_approved_flight(
    client, auth_headers, test_ops, approved_flight
):
    headers = await auth_headers(test_ops)
    approved = await client.post(
        f"/api/flights/{approved_flight.get('id')}/approve",
        json={},
        headers=headers,
    )
    assert approved.status_code == 400


@pytest.mark.asyncio
async def test_ops_approve_non_existent_flight(
    client,
    auth_headers,
    test_ops,
):
    headers = await auth_headers(test_ops)
    fake_id = "2b05c58d-7680-434a-bb05-2cf85ef32966"
    approved = await client.post(
        f"/api/flights/{fake_id}/approve",
        json={},
        headers=headers,
    )
    assert approved.status_code == 404


@pytest.mark.asyncio
async def test_ops_void_flight(client, auth_headers, test_ops, pending_flight):
    headers = await auth_headers(test_ops)
    voided = await client.post(
        f"/api/flights/{pending_flight.get('id')}/void",
        json={"void_reason": "Wrong flight date"},
        headers=headers,
    )
    assert voided.status_code == 200
    assert voided.json().get("status") == "Voided"


@pytest.mark.asyncio
async def test_pilot_void_flight(client, auth_headers, test_pilot, pending_flight):
    headers = await auth_headers(test_pilot)
    voided = await client.post(
        f"/api/flights/{pending_flight.get('id')}/void",
        json={"void_reason": "Wrong flight date"},
        headers=headers,
    )
    assert voided.status_code == 403


@pytest.mark.asyncio
async def test_ops_void_already_voided_flight(
    client, auth_headers, test_ops, voided_flight
):
    headers = await auth_headers(test_ops)
    voided = await client.post(
        f"/api/flights/{voided_flight.get('id')}/void",
        json={
            "void_reason": "Wrong flight date",
        },
        headers=headers,
    )
    assert voided.status_code == 400


@pytest.mark.asyncio
async def test_ops_void_non_existent_flight(
    client,
    auth_headers,
    test_ops,
):
    headers = await auth_headers(test_ops)
    fake_id = "2b05c58d-7680-434a-bb05-2cf85ef32966"
    voided = await client.post(
        f"/api/flights/{fake_id}/void",
        json={
            "void_reason": "Wrong timing",
        },
        headers=headers,
    )
    assert voided.status_code == 404
