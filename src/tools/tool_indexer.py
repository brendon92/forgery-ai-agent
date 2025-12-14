from typing import List, Dict
import os
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from langchain_core.tools import BaseTool

class ToolIndexer:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection_name = "mcp_tools"
        
        # Initialize Vector Store
        self.vector_store = Qdrant.from_existing_collection(
            embedding=self.embeddings,
            collection_name=self.collection_name,
            url=self.qdrant_url
        )

    def index_tools(self, tools: List[BaseTool]):
        """
        Indexes a list of LangChain/MCP tools into Qdrant.
        """
        texts = []
        metadatas = []
        
        for tool in tools:
            # Create a rich semantic description
            text = f"Tool Name: {tool.name}\nDescription: {tool.description}\nArgs: {tool.args}"
            texts.append(text)
            
            # Store the full tool definition in metadata so we can reconstruct/route to it
            metadatas.append({
                "tool_name": tool.name,
                "description": tool.description,
                "json_schema": str(tool.args) # simplified storage
            })
            
        print(f"Indexing {len(tools)} tools into Qdrant...")
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        print("Tool indexing complete.")

    def delete_all_tools(self):
        """Clears the tool index (useful for refreshing registry)"""
        # Logic to clear collection would go here
        pass
