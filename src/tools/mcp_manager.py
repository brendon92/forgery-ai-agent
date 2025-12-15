import asyncio
import os
import shutil
from typing import List, Dict, Optional
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
from contextlib import AsyncExitStack

from src.tools.tool_indexer import ToolIndexer
# We will use this to persist config
# from src.memory.graph_store import ... (Using Neo4j directly via driver if needed or via a ConfigService)

class MCPServerManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MCPServerManager, cls).__new__(cls)
            cls._instance.connections = {} # key: server_name, value: stacks/sessions
            cls._instance.indexer = ToolIndexer()
        return cls._instance

    async def connect_server(self, name: str, command: str, args: List[str], env: Optional[Dict] = None):
        """
        Connects to an MCP server via Stdio.
        """
        print(f"Connecting to MCP server '{name}'...")
        
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env={**os.environ, **(env or {})}
        )
        
        # managing the context stack manually to keep connection alive
        stack = AsyncExitStack()
        try:
            read, write = await stack.enter_async_context(stdio_client(server_params))
            session = await stack.enter_async_context(ClientSession(read, write))
            
            await session.initialize()
            
            # List tools
            result = await session.list_tools()
            tools = result.tools
            
            # Index tools
            # We need to adapt MCP tools to the format expected by ToolIndexer
            # ToolIndexer expects LangChain BaseTool-like objects or we adapt index_tools
            # For now, let's create a wrapper object
            class MCPToolWrapper:
                def __init__(self, t):
                    self.name = t.name
                    self.description = t.description
                    self.args = t.inputSchema
            
            wrapped_tools = [MCPToolWrapper(t) for t in tools]
            self.indexer.index_tools(wrapped_tools)
            
            self.connections[name] = {
                "stack": stack,
                "session": session,
                "tools": {t.name: t for t in tools}
            }
            print(f"Connected to '{name}' and indexed {len(tools)} tools.")
            
        except Exception as e:
            print(f"Failed to connect to '{name}': {e}")
            await stack.aclose()
            raise e

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict):
        if server_name not in self.connections:
            raise ValueError(f"Server '{server_name}' not connected.")
            
        session: ClientSession = self.connections[server_name]["session"]
        result = await session.call_tool(tool_name, arguments)
        return result

    async def disconnect_all(self):
        for name, conn in self.connections.items():
            print(f"Disconnecting '{name}'...")
            await conn["stack"].aclose()
        self.connections.clear()

# Global instance
mcp_manager = MCPServerManager()
