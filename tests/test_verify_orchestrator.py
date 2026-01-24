import pytest
import asyncio
from servicenow_api.servicenow_agent import create_agents

def test_create_agents_structure():
    """
    Verifies that create_agents returns an orchestrator with the expected delegation tools.
    """
    agent = create_agents(
        mcp_config=None,
        mcp_url=None,
        skills_directory=None 
    )
    
    print("\nAttempting to run agent lightly (dry run) or inspect tools...")
    
    # We can inspect _function_toolset to see if tools are registered
    print("Inspecting _function_toolset...")
    if hasattr(agent, '_function_toolset'):
        ft = agent._function_toolset
        
        found_tools = []
        if hasattr(ft, 'tools'):
             found_tools = list(ft.tools.keys())
        elif hasattr(ft, 'definitions'):
             found_tools = [d.name for d in ft.definitions]
        
        print("Found tools in _function_toolset:", found_tools)
        
        expected_tags = [
            "application",
            "cmdb",
            "cicd",
            "plugins",
            "source_control",
            "testing",
            "update_sets",
            "change_management",
            "import_sets",
            "incidents",
            "knowledge_management",
            "table_api",
            "custom_api",
            "auth",
        ]
        
        for tag in expected_tags:
            expected_tool_name = f"delegate_to_{tag}_agent"
            assert expected_tool_name in found_tools, f"Missing tool: {expected_tool_name}"
            
        print("SUCCESS: All delegation tools verified on the Orchestrator.")
    else:
        pytest.fail("Agent does not have _function_toolset attribute to inspect.")

if __name__ == "__main__":
    test_create_agents_structure()
