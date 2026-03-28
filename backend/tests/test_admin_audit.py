import pytest


@pytest.mark.asyncio
async def test_admin_can_list_audit_logs(client, test_admin, pending_flight, auth_headers):
    headers = await auth_headers(test_admin)

    result = await client.get("/api/admin/audit/logs", headers=headers)

    assert result.status_code == 200


@pytest.mark.asyncio
async def test_admin_can_get_audit_log_by_id(
    client, test_admin, pending_flight, auth_headers
):
    headers = await auth_headers(test_admin)

    logs = await client.get("/api/admin/audit/logs", headers=headers)
    log_id = logs.json().get("items")[0].get("id")

    result = await client.get(f"/api/admin/audit/logs/{log_id}", headers=headers)

    assert result.status_code == 200


@pytest.mark.asyncio
async def test_ops_denied_audit_logs(client, test_ops, auth_headers):
    headers = await auth_headers(test_ops)

    result = await client.get("/api/admin/audit/logs", headers=headers)

    assert result.status_code == 403


@pytest.mark.asyncio
async def test_ops_denied_audit_log_by_id(
    client, test_admin, test_ops, pending_flight, auth_headers
):
    admin_headers = await auth_headers(test_admin)
    logs = await client.get("/api/admin/audit/logs", headers=admin_headers)
    log_id = logs.json().get("items")[0].get("id")

    ops_headers = await auth_headers(test_ops)
    result = await client.get(f"/api/admin/audit/logs/{log_id}", headers=ops_headers)

    assert result.status_code == 403


@pytest.mark.asyncio
async def test_pilot_denied_audit_logs(client, test_pilot, auth_headers):
    headers = await auth_headers(test_pilot)

    result = await client.get("/api/admin/audit/logs", headers=headers)

    assert result.status_code == 403


@pytest.mark.asyncio
async def test_unauthenticated_denied_audit_logs(client):
    result = await client.get("/api/admin/audit/logs")

    assert result.status_code == 401


@pytest.mark.asyncio
async def test_audit_logs_correct_total(
    client, test_admin, pending_flight, approved_flight, auth_headers
):
    headers = await auth_headers(test_admin)

    result = await client.get("/api/admin/audit/logs", headers=headers)

    assert result.status_code == 200
    assert result.json().get("total") >= 2


@pytest.mark.asyncio
async def test_audit_logs_actor_filter(
    client, test_admin, test_pilot, pending_flight, auth_headers
):
    headers = await auth_headers(test_admin)

    result = await client.get(
        f"/api/admin/audit/logs?actor_filter={test_pilot.id}", headers=headers
    )

    assert result.status_code == 200
    data = result.json()
    assert data.get("total") >= 1
    for log in data.get("items"):
        assert log.get("actor_id") == str(test_pilot.id)


@pytest.mark.asyncio
async def test_audit_logs_target_filter(
    client, test_admin, pending_flight, auth_headers
):
    headers = await auth_headers(test_admin)

    flight_id = pending_flight.get("id")
    result = await client.get(
        f"/api/admin/audit/logs?target_filter={flight_id}", headers=headers
    )

    assert result.status_code == 200
    data = result.json()
    assert data.get("total") >= 1
    for log in data.get("items"):
        assert log.get("target_id") == flight_id


@pytest.mark.asyncio
async def test_audit_logs_action_filter(
    client, test_admin, pending_flight, auth_headers
):
    headers = await auth_headers(test_admin)

    result = await client.get(
        "/api/admin/audit/logs?action_filter=FLIGHT_CREATED", headers=headers
    )

    assert result.status_code == 200
    data = result.json()
    assert data.get("total") >= 1
    for log in data.get("items"):
        assert log.get("action") == "FLIGHT_CREATED"



@pytest.mark.asyncio
async def test_detailed_audit_log_actor_username(
    client, test_admin, test_pilot, pending_flight, auth_headers
):
    headers = await auth_headers(test_admin)

    logs = await client.get(
        "/api/admin/audit/logs?action_filter=FLIGHT_CREATED", headers=headers
    )
    log_id = logs.json().get("items")[0].get("id")

    result = await client.get(f"/api/admin/audit/logs/{log_id}", headers=headers)

    assert result.status_code == 200
    assert result.json().get("actor_username") == test_pilot.username


@pytest.mark.asyncio
async def test_detailed_audit_log_target_type_flight(
    client, test_admin, pending_flight, auth_headers
):
    headers = await auth_headers(test_admin)

    logs = await client.get(
        "/api/admin/audit/logs?action_filter=FLIGHT_CREATED", headers=headers
    )
    log_id = logs.json().get("items")[0].get("id")

    result = await client.get(f"/api/admin/audit/logs/{log_id}", headers=headers)

    assert result.status_code == 200
    assert result.json().get("target_type") == "Flight"


@pytest.mark.asyncio
async def test_detailed_audit_log_not_found(client, test_admin, auth_headers):
    headers = await auth_headers(test_admin)

    result = await client.get(
        "/api/admin/audit/logs/91bd6508-1c57-4807-8c6b-22613c25b164", headers=headers
    )

    assert result.status_code == 404
