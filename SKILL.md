---
name: autocar-api
description: Skill for interacting with the AutoCar Software API (USR v2.0) with explicit tools for each entity.
---

# AutoCar API Connector (USR v2.0)

This skill provides explicit tools for managing the AutoCar Software API. It uses the ISLI Universal Skill Runtime (USR) v2.0 standard.

## Primary Tools

### `login`
Authenticate with your staff account.

**Parameters:**
- `email`: Your staff email.
- `password`: Your staff password.

### Entity Tools (CRUD)
The skill provides specific tools for **Customers, Invoices, Parts, WorkOrders, Vehicles, PurchaseOrders, Suppliers, Categories, and Staff**.

Standard pattern for each entity (e.g., `customer`):
- `list_customers`: Get all customers.
- `get_customer`: Get a customer by `id`.
- `create_customer`: Create a new customer using a `data` object.
- `update_customer`: Update a customer using an `id` and a `data` object.
- `delete_customer`: Remove a customer by `id`.

---

## Procedural Instructions for AI Agent

1. **Authentication**: If you aren't logged in, use the `login` tool first.
2. **Task Execution**:
   - To list items, use the `list_<entity>s` tool.
   - To find a specific record, use `get_<entity>`.
   - To create or update, use `create_<entity>` or `update_<entity>` with the appropriate `data` JSON object.
3. **Internal Auth**: All requests are automatically signed with `X-Internal-Auth`. The skill manages your session tokens internally.
