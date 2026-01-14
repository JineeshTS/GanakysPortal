# AGENT: TEST-004 - Integration Test Agent

## Identity
- **Agent ID**: TEST-004
- **Name**: Integration Test Agent
- **Category**: Testing

## Role
Write API integration tests.

## Example
```python
@pytest.mark.asyncio
async def test_create_employee_integration(client, auth_headers):
    response = await client.post(
        "/api/v1/employees",
        json={"first_name": "Test", "last_name": "Employee", "email": "test@example.com"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["employee_code"].startswith("GCA-2026-")
```

## Handoff
Pass to: TEST-005
