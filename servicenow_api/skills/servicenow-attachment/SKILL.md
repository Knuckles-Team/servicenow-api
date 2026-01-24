---
name: ServiceNow Attachment
description: Capabilities for managing attachments in ServiceNow.
---

# ServiceNow Attachment

This skill allows the agent to upload, retrieve, and delete attachments in ServiceNow.

## Tools

### `get_attachment`

- **Description**: Retrieves attachment metadata.
- **Parameters**:
    - `sys_id` (str): Attachment Sys ID.

### `upload_attachment`

- **Description**: Uploads an attachment to a record.
- **Parameters**:
    - `file_path` (str): Absolute path to the file to upload.
    - `table_name` (str): Table name associated with the attachment.
    - `table_sys_id` (str): Sys ID of the record in the table.
    - `file_name` (str): Name of the file.
    - `content_type` (Optional[str]): MIME type of the file.

### `delete_attachment`

- **Description**: Deletes an attachment.
- **Parameters**:
    - `sys_id` (str): Attachment Sys ID.

## Usage

### Uploading an Attachment

```python
result = upload_attachment(
    file_path="/path/to/file.txt",
    table_name="incident",
    table_sys_id="sys_id_of_incident",
    file_name="file.txt"
)
```
