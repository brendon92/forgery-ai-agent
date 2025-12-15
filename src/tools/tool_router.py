from typing import List, Dict, Any
import json
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings

class SemanticToolRouter:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        try:
            self.vector_store = Qdrant.from_existing_collection(
                embedding=self.embeddings,
                collection_name="mcp_tools",
                url="http://localhost:6333"
            )
        except Exception:
            print("Warning: 'mcp_tools' collection not found in Qdrant. Tool routing will be disabled until tools are indexed.")
            # Fallback or allow it to be None
            self.vector_store = None

    def route(self, query: str) -> List[Dict[str, Any]]:
        """
        Routes the user query to the top-k most relevant tools.
        Returns a list of tool definitions (names/descriptions) to be passed to the Agent.
        """
        print(f"Routing query: '{query}'...")
        
        if not self.vector_store:
            print("Vector store not available. Returning empty tool list.")
            return []
            
        # Perform similarity search
        try:
            results = self.vector_store.similarity_search(query, k=self.top_k)
        except Exception as e:
            print(f"Tool routing failed: {e}")
            return []
        
        shortlisted_tools = []
        for doc in results:
            # print(f" - Found tool: {doc.metadata.get('tool_name')}")
            tool_def = {
                "name": doc.metadata.get("tool_name"),
                "description": doc.metadata.get("description"),
            }
            
            # Try to parse properties/args if available
            if "json_schema" in doc.metadata:
                try:
                    schema = doc.metadata.get("json_schema")
                    if isinstance(schema, str):
                        tool_def["args"] = json.loads(schema)
                    else:
                        tool_def["args"] = schema
                except json.JSONDecodeError:
                    print(f"Failed to parse JSON schema for tool: {tool_def['name']}")
                    tool_def["args"] = {}
                except Exception as e:
                    print(f"Error processing tool schema: {e}")
                    
            shortlisted_tools.append(tool_def)
            
        return shortlisted_tools
