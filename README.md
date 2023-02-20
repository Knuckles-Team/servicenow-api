# ServiceNow API
*Version: 0.11.0*

ServiceNow API Python Wrapper

This repository is actively maintained and will continue adding more API calls

### API Calls:
- Table
- CI/CD
- Import Sets

Coming Soon:
- Incident
- CMDB
- Application Service

### Usage:

```python
#!/usr/bin/python
# coding: utf-8
import servicenow_api

username = "<SERVICENOW USERNAME>"
password = "<SERVICENOW PASSWORD>"
servicenow_api_url = "<SERVICENOW_URL>"
client = servicenow_api.Api(url=servicenow_api_url, username=username, password=password)

table = client.get_table(table="<TABLE NAME>")
print(f"Table: {table}")
```

#### Install Instructions
Install Python Package

```bash
python -m pip install servicenow-api
```

#### Build Instructions
Build Python Package

```bash
sudo chmod +x ./*.py
pip install .
python setup.py bdist_wheel --universal
# Test Pypi
twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose -u "Username" -p "Password"
# Prod Pypi
twine upload dist/* --verbose -u "Username" -p "Password"
```
