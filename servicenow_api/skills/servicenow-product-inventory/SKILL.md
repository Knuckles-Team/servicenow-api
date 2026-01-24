---
name: ServiceNow Product Inventory
description: Manage and query product inventory.
---

# Product Inventory

This skill allows the agent to interact with the ServiceNow Product Inventory API.

## Capabilities

- **Get Product Inventory**: Retrieve product inventory records with various filters.
- **Delete Product Inventory**: Delete a product inventory record.

## Tools

### `get_product_inventory`
Retrieves product inventory.

**Parameters:**
- `customer` (optional): Filter by customer ID.
- `place_id` (optional): Filter by location ID.
- `status` (optional): Filter by status (e.g., 'active').
- `limit` (optional): Max records.
- `offset` (optional): Pagination offset.

### `delete_product_inventory`
Deletes a product inventory record.

**Parameters:**
- `id`: The Sys ID of the product inventory record.

## Examples

### List Active Products for Customer
```python
get_product_inventory(customer="customer_sys_id", status="active")
```

### Delete Product
```python
delete_product_inventory(id="product_sys_id")
```
