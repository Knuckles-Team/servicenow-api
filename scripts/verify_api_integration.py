#!/usr/bin/env python3
import ast
import glob
import os
import sys

BASELINES = {
    "adguard-home-agent": 89.2,
    "ansible-tower-mcp": 94.7,
    "archivebox-api": 85.7,
    "documentdb-mcp": 100.0,
    "github-agent": 100.0,
    "gitlab-api": 6.4,
    "home-assistant-agent": 63.6,
    "jellyfin-mcp": 81.0,
    "langfuse-agent": 100.0,
    "listmonk-api": 87.5,
    "mealie-mcp": 96.4,
    "microsoft-agent": 99.6,
    "nextcloud-agent": 52.6,
    "owncast-agent": 100.0,
    "plane-agent": 54.9,
    "portainer-agent": 35.5,
    "postiz-agent": 0.0,
    "qbittorrent-agent": 70.8,
    "scholarx": 90.0,
    "servicenow-api": 73.1,
    "stirlingpdf-agent": 0.0,
    "wger-agent": 41.7,
}


def parse_api_client(filepath):
    """
    Parses api_client.py to find the main API/Client class and its public methods.
    Returns a set of method names.
    """
    with open(filepath, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    methods = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Focus on Api or Client classes
            class_name = node.name.lower()
            if "api" in class_name or "client" in class_name or node.name == "Api":
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        # Filter out private methods and constructor
                        if (
                            not item.name.startswith("_")
                            and item.name != "authenticate"
                        ):
                            methods[item.name] = {
                                "line": item.lineno,
                                "class": node.name,
                            }
    return methods


class MethodCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.called_methods = set()
        self.action_literals = set()

    def visit_Attribute(self, node):
        # E.g. client.get_repositories
        if isinstance(node.value, ast.Name):
            # Typically client, api, self
            if node.value.id in ("client", "api", "self"):
                self.called_methods.add(node.attr)
        self.generic_visit(node)

    def visit_Call(self, node):
        # E.g. getattr(client, "foo")
        if isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if len(node.args) >= 2 and isinstance(node.args[0], ast.Name):
                if node.args[0].id in ("client", "api"):
                    if isinstance(node.args[1], ast.Constant):
                        self.called_methods.add(node.args[1].value)
        self.generic_visit(node)

    def visit_Compare(self, node):
        # Capture action comparisons, e.g. action == "get"
        for op, comparator in zip(node.ops, node.comparators, strict=False):
            if isinstance(op, (ast.Eq, ast.In)):
                if isinstance(comparator, ast.Constant) and isinstance(
                    comparator.value, str
                ):
                    self.action_literals.add(comparator.value)
        self.generic_visit(node)


def parse_mcp_server(filepath, api_methods):
    """
    Parses mcp_server.py to extract registered tools and identify which
    api_methods they leverage.
    """
    with open(filepath, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filepath)

    tool_mappings = {}
    all_mapped_methods = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check if this function is a tool (e.g. decorated with mcp.tool)
            is_tool = False
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call):
                    func = dec.func
                    if isinstance(func, ast.Attribute) and func.attr == "tool":
                        is_tool = True
                elif isinstance(dec, ast.Attribute) and dec.attr == "tool":
                    is_tool = True

            if (
                is_tool
                or node.name.startswith("github_")
                or node.name.startswith("gitlab_")
                or node.name.startswith("adguard_")
                or node.name.startswith("atlassian_")
            ):
                visitor = MethodCallVisitor()
                visitor.visit(node)
                # Find which of the visited methods are in our api_methods list
                mapped = visitor.called_methods.intersection(api_methods.keys())
                tool_mappings[node.name] = {
                    "methods": list(mapped),
                    "actions": list(visitor.action_literals),
                }
                all_mapped_methods.update(mapped)

    return tool_mappings, all_mapped_methods


def verify_agent(agent_dir):
    # Find api_client.py and mcp_server.py
    api_clients = glob.glob(
        os.path.join(agent_dir, "**", "api_client.py"), recursive=True
    )
    mcp_servers = glob.glob(
        os.path.join(agent_dir, "**", "mcp_server.py"), recursive=True
    )

    if not api_clients or not mcp_servers:
        return None

    api_client_path = api_clients[0]
    mcp_server_path = mcp_servers[0]

    api_methods = parse_api_client(api_client_path)
    if not api_methods:
        return None

    tool_mappings, mapped_methods = parse_mcp_server(mcp_server_path, api_methods)

    total_methods = len(api_methods)
    covered_methods = len(mapped_methods)
    coverage = (covered_methods / total_methods) * 100 if total_methods > 0 else 0.0

    unmapped = set(api_methods.keys()) - mapped_methods

    return {
        "agent_name": os.path.basename(agent_dir),
        "api_client": api_client_path,
        "mcp_server": mcp_server_path,
        "total_methods": total_methods,
        "covered_methods": covered_methods,
        "coverage": coverage,
        "unmapped": sorted(list(unmapped)),
        "mapped": sorted(list(mapped_methods)),
        "tool_mappings": tool_mappings,
    }


def main():
    args = sys.argv[1:]

    # --- Local Mode (Single Agent Validation) ---
    if "--local" in args or "--pre-commit" in args:
        cwd = os.getcwd()
        res = verify_agent(cwd)
        if not res:
            # If no client or server found in this dir, pass silently (e.g. non-python files, doc edits)
            print(
                "Skipping integration parity verification: No mcp_server.py/api_client.py found in current directory."
            )
            sys.exit(0)

        agent_name = res["agent_name"]
        coverage = res["coverage"]
        baseline = BASELINES.get(agent_name, 0.0)

        print(f"=== API-to-MCP Integration Parity Check for: {agent_name} ===")
        print(f"- API client methods: {res['total_methods']}")
        print(f"- Integrated methods: {res['covered_methods']}")
        print(f"- Current Coverage  : {coverage:.1f}%")
        print(f"- Target Baseline   : {baseline:.1f}%")

        # Allow small floating point tolerance (0.05%)
        if coverage < (baseline - 0.05):
            print(
                f"\n❌ FAILED: Integration coverage ({coverage:.1f}%) has DEGRADED below the required baseline of {baseline:.1f}%!"
            )
            print(
                "Please ensure any new or refactored API client methods are properly integrated into MCP server tools."
            )
            if res["unmapped"]:
                print("\nUnmapped API methods:")
                for m in res["unmapped"]:
                    print(f"  - {m}")
            sys.exit(1)
        else:
            print(
                "\n✅ PASSED: Integration coverage meets or exceeds the required baseline!"
            )
            sys.exit(0)

    # --- Default Mode (Workspace-wide Scan) ---
    agents_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    agent_dirs = [
        d for d in glob.glob(os.path.join(agents_dir, "*")) if os.path.isdir(d)
    ]

    # Also support nested subdirectories if any
    nested_dirs = [
        d for d in glob.glob(os.path.join(agents_dir, "*", "*")) if os.path.isdir(d)
    ]
    all_agent_dirs = sorted(list(set(agent_dirs + nested_dirs)))

    results = []
    for agent_dir in all_agent_dirs:
        # Avoid directories starting with dot or venv
        if (
            os.path.basename(agent_dir).startswith(".")
            or "venv" in agent_dir
            or "egg-info" in agent_dir
        ):
            continue
        try:
            res = verify_agent(agent_dir)
            if res:
                results.append(res)
        except Exception as e:
            print(f"Operation failed: {type(e).__name__}", file=sys.stderr)

    # Print a beautiful report
    print("# API to MCP Integration Parity Report")
    print(f"Scan Directory: `{agents_dir}`\n")
    print("| Agent Name | API Methods | Covered Methods | Coverage % | Status |")
    print("|---|---|---|---|---|")

    for r in results:
        status = "✅ 100%" if r["coverage"] >= 100.0 else "⚠️ Parity Gap"
        print(
            f"| {r['agent_name']} | {r['total_methods']} | {r['covered_methods']} | {r['coverage']:.1f}% | {status} |"
        )

    print("\n## Detailed Parity Gaps\n")
    for r in results:
        if r["coverage"] < 100.0:
            print(f"### ⚠️ {r['agent_name']} ({r['coverage']:.1f}% Integration)")
            print(f"- **API Client**: `{os.path.relpath(r['api_client'], agents_dir)}`")
            print(f"- **MCP Server**: `{os.path.relpath(r['mcp_server'], agents_dir)}`")
            print("- **Unmapped API Methods**:")
            for m in r["unmapped"]:
                print(f"  - `{m}`")
            print()
        else:
            print(f"### ✅ {r['agent_name']} (100% Integration)")
            print(
                f"- All {r['total_methods']} methods successfully mapped to MCP tools."
            )
            print()


if __name__ == "__main__":
    main()
