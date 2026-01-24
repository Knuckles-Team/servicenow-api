---
name: ServiceNow Service Qualification
description: Validates technical service availability and eligibility.
---

# Service Qualification

This skill allows the agent to interact with the ServiceNow Technical Service Qualification API.

## Capabilities

- **Check Service Qualification**: Create a qualification request to check if a service can be provided.
- **Get Service Qualification**: Retrieve the details and status of a qualification request.
- **Process Qualification Result**: (Advanced) Process the results of a qualification check.

## Tools

### `check_service_qualification`
Creates a technical service qualification request.

**Parameters:**
- `description` (optional): Description of the request.
- `externalId` (optional): External reference ID.
- `relatedParty` (list): List of related parties (Customer, etc.).
- `serviceQualificationItem` (list): List of items to qualify.

### `get_service_qualification`
Retrieves a qualification request.

**Parameters:**
- `id` (optional): The Sys ID or External ID of the qualification request.
- `state` (optional): Filter by state.

### `process_service_qualification_result`
Processes the result of a qualification.

**Parameters:**
- `serviceQualificationItem` (list): The items with qualification results.
- `description` (optional): Description.

## Examples

### Check Qualification
```python
check_service_qualification(
    description="Check feasibility for SD-WAN",
    relatedParty=[
        {"id": "customer_sys_id", "@referredType": "Customer", "@type": "RelatedParty"}
    ],
    serviceQualificationItem=[
        {
            "id": "item_1",
            "service": {
                "serviceSpecification": {
                    "id": "sd_wan_spec_id"
                }
            }
        }
    ]
)
```

### Get Qualification Status
```python
get_service_qualification(id="qual_req_sys_id")
```
