# ServiceNow API

![PyPI - Version](https://img.shields.io/pypi/v/servicenow-api)
![PyPI - Downloads](https://img.shields.io/pypi/dd/servicenow-api)
![GitHub Repo stars](https://img.shields.io/github/stars/Knuckles-Team/servicenow-api)
![GitHub forks](https://img.shields.io/github/forks/Knuckles-Team/servicenow-api)
![GitHub contributors](https://img.shields.io/github/contributors/Knuckles-Team/servicenow-api)
![PyPI - License](https://img.shields.io/pypi/l/servicenow-api)
![GitHub](https://img.shields.io/github/license/Knuckles-Team/servicenow-api)

![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/Knuckles-Team/servicenow-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Knuckles-Team/servicenow-api)
![GitHub closed pull requests](https://img.shields.io/github/issues-pr-closed/Knuckles-Team/servicenow-api)
![GitHub issues](https://img.shields.io/github/issues/Knuckles-Team/servicenow-api)

![GitHub top language](https://img.shields.io/github/languages/top/Knuckles-Team/servicenow-api)
![GitHub language count](https://img.shields.io/github/languages/count/Knuckles-Team/servicenow-api)
![GitHub repo size](https://img.shields.io/github/repo-size/Knuckles-Team/servicenow-api)
![GitHub repo file count (file type)](https://img.shields.io/github/directory-file-count/Knuckles-Team/servicenow-api)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/servicenow-api)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/servicenow-api)

*Version: 1.1.2*

ServiceNow API Python Wrapper

This repository is actively maintained and will continue adding more API calls

This can run as a standalone MCP Server for Agentic AI!

Contributions are welcome!

All API Response objects are customized for the response call.
You can get all return values in a parent.value.nested_value format,
or you can run parent.model_dump() to get the table in dictionary format.

#### API Calls:
- Application Service
- Change Management
- CI/CD
- CMDB
- Import Sets
- Incident
- Knowledge Base
- Table
- Custom Endpoint

If your API call isn't supported, you can always run the standard custom API endpoint function to get/post/put/delete and endpoint

<details>
  <summary><b>Usage:</b></summary>

OAuth Authentication

```python
#!/usr/bin/python
# coding: utf-8
import servicenow_api

username = "<SERVICENOW USERNAME>"
password = "<SERVICENOW PASSWORD>"
client_id = "<SERVICENOW CLIENT_ID>"
client_secret = "<SERVICENOW_CLIENT_SECRET>"
servicenow_url = "<SERVICENOW_URL>"

client = servicenow_api.Api(url=servicenow_url,
                            username=username,
                            password=password,
                            client_id=client_id,
                            client_secret=client_secret)

table = client.get_table(table="<TABLE NAME>")
print(f"Table: {table.model_dump()}")
```


Basic Authentication

```python
#!/usr/bin/python
# coding: utf-8
import servicenow_api

username = "<SERVICENOW USERNAME>"
password = "<SERVICENOW PASSWORD>"
servicenow_url = "<SERVICENOW_URL>"

client = servicenow_api.Api(url=servicenow_url,
                            username=username,
                            password=password)

table = client.get_table(table="<TABLE NAME>")
print(f"Table: {table.model_dump()}")
```

Proxy and SSL Verify

```python
#!/usr/bin/python
# coding: utf-8
import servicenow_api

username = "<SERVICENOW USERNAME>"
password = "<SERVICENOW PASSWORD>"
servicenow_url = "<SERVICENOW_URL>"

proxy = "https://proxy.net"

client = servicenow_api.Api(url=servicenow_url,
                            username=username,
                            password=password,
                            proxy=proxy,
                            verify=False)

table = client.get_table(table="<TABLE NAME>")
print(f"Table: {table.model_dump()}")
```

### Use with AI

Deploy MCP Server as a Service
```bash
docker pull knucklessg1/servicenow:latest
```

Modify the `compose.yml`

```compose
services:
  servicenow-mcp:
    image: knucklessg1/servicenow:latest
    environment:
      - HOST=0.0.0.0
      - PORT=8004
    ports:
      - 8004:8004
```

Configure `mcp.json`

Recommended: Store secrets in environment variables with lookup in JSON file.

For Testing Only: Plain text storage will also work, although **not** recommended.

```json
{
  "mcpServers": {
    "servicenow": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "servicenow-api",
        "servicenow-mcp"
      ],
      "env": {
        "SERVICENOW_INSTANCE": "https://www.servicenow.com",
        "SERVICENOW_USERNAME": "user",
        "SERVICENOW_PASSWORD": "pass",
        "SERVICENOW_CLIENT_ID": "client_id",
        "SERVICENOW_CLIENT_SECRET": "client_secret",
        "SERVICENOW_VERIFY": "False"
      },
      "timeout": 200000
    }
  }
}

```

</details>

<details>
  <summary><b>Installation Instructions:</b></summary>

Install Python Package

```bash
python -m pip install servicenow-api
```

</details>

<details>
  <summary><b>Tests:</b></summary>

```bash
python ./test/test_servicenow_models.py
```
</details>


<img width="100%" height="180em" src="https://github-readme-stats.vercel.app/api?username=Knucklessg1&show_icons=true&hide_border=true&&count_private=true&include_all_commits=true" />

![GitHub followers](https://img.shields.io/github/followers/Knucklessg1)

![GitHub User's stars](https://img.shields.io/github/stars/Knucklessg1)

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/knuckles-team-servicenow-api-badge.png)](https://mseep.ai/app/knuckles-team-servicenow-api)
