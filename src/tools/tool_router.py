from typing import List, Dict, Any
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
        
        # Perform similarity search
        results = self.vector_store.similarity_search(query, k=self.top_k)
        
        shortlisted_tools = []
        for doc in results:
            print(f" - Found tool: {doc.metadata.get('tool_name')}")
            shortlisted_tools.append({
                "name": doc.metadata.get("tool_name"),
                "description": doc.metadata.get("description"),
                # We could include the full schema here if needed for direct binding
                # "args": doc.metadata.get("json_schema") 
            })
            
        return shortlisted_tools
