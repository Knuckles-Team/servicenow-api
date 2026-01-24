---
name: ServiceNow Email
description: Capabilities for sending and retrieving emails in ServiceNow.
---

# ServiceNow Email

This skill allows the agent to interact with the ServiceNow Email API to send and retrieve email messages.

## Tools

### `send_email`

- **Description**: Sends an email via ServiceNow.
- **Parameters**:
    - `to` (Union[str, List[str]]): Recipient email addresses.
    - `subject` (Optional[str]): Email subject.
    - `text` (Optional[str]): Email body text.
    - `html` (Optional[str]): Email body HTML.

## Usage

### Sending an Email

```python
result = send_email(
    to=["user@example.com"],
    subject="Test Email",
    text="This is a test email sent from ServiceNow Agent."
)
```
