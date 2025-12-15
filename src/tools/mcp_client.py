# LEGACY STUB
# This file is being replaced by src/tools/mcp_manager.py which uses the official SDK.
# Keeping this stub to avoid breaking imports elsewhere temporarily.

class MCPClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.tools = []

    async def connect(self):
        print(f"Connecting to MCP server at {self.server_url} (Legacy Client)...")
        self.tools = []

    async def list_tools(self):
        return self.tools

    async def call_tool(self, tool_name: str, arguments: dict):
        return "Legacy MCPClient is deprecated. Use MCPServerManager."

mcp_client = MCPClient("dummy")
