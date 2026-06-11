---
name: autocar-api
description: Stateless skill for interacting with the AutoCar Software API (FastAPI, Port 8101).
---

# AutoCar API Connector (Local Optimized)

This skill is a stateless FastAPI microservice designed for the local ISLI architecture. It operates on port **8101** and manages AutoCar API interactions by requiring the AI agent to pass tokens explicitly.

## Core Tools

### `login`
Authenticate with staff credentials. 
- **Returns**: `accessToken` and `refreshToken`.
- **Note**: You must save these tokens in your context.

### Entity Tools (45+ Tools)
Specific tools for **Customers, Invoices, Parts, WorkOrders, Vehicles, PurchaseOrders, Suppliers, Categories, and Staff**.

**Stateless Pattern**:
Every tool call (except `login`) requires an `access_token` parameter in the payload.

Example: `get_customer`
```json
{
  "id": "GUID_HERE",
  "access_token": "TOKEN_FROM_LOGIN"
}
```

Example: `list_invoices`
```json
{
  "access_token": "TOKEN_FROM_LOGIN"
}
```

---

## Procedural Instructions for AI Agent

1. **Discovery**: This skill runs on port **8101**. Use tools as defined in `isli-skill.yaml`.
2. **Stateless Auth**:
   - Call `login` first.
   - Extract the `accessToken` from the response.
   - For every subsequent call, you **MUST** include `"access_token": "..."` in the JSON payload.
3. **Health**: The container includes a Docker `HEALTHCHECK` and a `/health` endpoint for architecture compliance.
