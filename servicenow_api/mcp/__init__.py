"""MCP tool registration modules for servicenow-api.

Auto-generated during ecosystem standardization.
Each domain has its own module with a register_*_tools function.
"""

from servicenow_api.mcp.mcp_account import register_account_tools
from servicenow_api.mcp.mcp_activity_subscriptions import (
    register_activity_subscriptions_tools,
)
from servicenow_api.mcp.mcp_aggregate import register_aggregate_tools
from servicenow_api.mcp.mcp_application import register_application_tools
from servicenow_api.mcp.mcp_attachment import register_attachment_tools
from servicenow_api.mcp.mcp_auth import register_auth_tools
from servicenow_api.mcp.mcp_batch import register_batch_tools
from servicenow_api.mcp.mcp_change_management import register_change_management_tools
from servicenow_api.mcp.mcp_cicd import register_cicd_tools
from servicenow_api.mcp.mcp_cilifecycle import register_cilifecycle_tools
from servicenow_api.mcp.mcp_cmdb import register_cmdb_tools
from servicenow_api.mcp.mcp_custom_api import register_custom_api_tools
from servicenow_api.mcp.mcp_data_classification import (
    register_data_classification_tools,
)
from servicenow_api.mcp.mcp_devops import register_devops_tools
from servicenow_api.mcp.mcp_email import register_email_tools
from servicenow_api.mcp.mcp_flows import register_flows_tools
from servicenow_api.mcp.mcp_hr import register_hr_tools
from servicenow_api.mcp.mcp_import_sets import register_import_sets_tools
from servicenow_api.mcp.mcp_incidents import register_incidents_tools
from servicenow_api.mcp.mcp_knowledge_management import (
    register_knowledge_management_tools,
)
from servicenow_api.mcp.mcp_metricbase import register_metricbase_tools
from servicenow_api.mcp.mcp_misc import register_misc_tools
from servicenow_api.mcp.mcp_plugins import register_plugins_tools
from servicenow_api.mcp.mcp_ppm import register_ppm_tools
from servicenow_api.mcp.mcp_product_inventory import register_product_inventory_tools
from servicenow_api.mcp.mcp_service_qualification import (
    register_service_qualification_tools,
)
from servicenow_api.mcp.mcp_source_control import register_source_control_tools
from servicenow_api.mcp.mcp_table_api import register_table_api_tools
from servicenow_api.mcp.mcp_testing import register_testing_tools
from servicenow_api.mcp.mcp_update_sets import register_update_sets_tools

__all__ = [
    "register_account_tools",
    "register_activity_subscriptions_tools",
    "register_aggregate_tools",
    "register_application_tools",
    "register_attachment_tools",
    "register_auth_tools",
    "register_batch_tools",
    "register_change_management_tools",
    "register_cicd_tools",
    "register_cilifecycle_tools",
    "register_cmdb_tools",
    "register_custom_api_tools",
    "register_data_classification_tools",
    "register_devops_tools",
    "register_email_tools",
    "register_flows_tools",
    "register_hr_tools",
    "register_import_sets_tools",
    "register_incidents_tools",
    "register_knowledge_management_tools",
    "register_metricbase_tools",
    "register_misc_tools",
    "register_plugins_tools",
    "register_ppm_tools",
    "register_product_inventory_tools",
    "register_service_qualification_tools",
    "register_source_control_tools",
    "register_table_api_tools",
    "register_testing_tools",
    "register_update_sets_tools",
]
