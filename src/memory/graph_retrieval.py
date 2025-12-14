from typing import List, Any
from llama_index.core import PropertyGraphIndex
from llama_index.core.indices.property_graph import GraphQRAGRetriever

class GraphRetrievalSystem:
    def __init__(self, index: PropertyGraphIndex):
        self.index = index
        # Initialize the GraphQRAGRetriever
        # This retriever uses the LLM to generate Cypher/Traversal queries
        # synonyms support can be added here
        self.retriever = self.index.as_retriever(
            similarity_top_k=5,
            # We can customize the retriever mode here (e.g., 'hybrid', 'keyword', 'vector')
            # For PropertyGraphIndex, 'guided' or 'auto' heavily relies on LLM
        )

    async def retrieve(self, query: str, workspace_id: str) -> List[Any]:
        """
        Execute a hybrid retrieval query scoped to a workspace.
        """
        print(f"Retrieving for query: '{query}' in workspace: {workspace_id}")
        
        # Note: LlamaIndex PropertyGraphIndex retriever handles the complexity:
        # 1. Vector search to find relevant nodes
        # 2. Traversal from those nodes
        # 3. Returning context
        
        # Future optimization: Inject workspace_id into the retrieval filter
        # Currently assuming the index handles all nodes, we might need 
        # to implement a custom retriever to strictly filter by workspace_id metadata
        
        nodes = await self.retriever.aretrieve(query)
        
        # Filter nodes by workspace_id if metadata is preserved (conceptual step)
        filtered_nodes = [
            node for node in nodes 
            if node.metadata.get("workspace_id") == workspace_id
        ]
        
        return filtered_nodes

    def query_graph_exact(self, cypher_query: str):
        """Allow direct Cypher queries for advanced reasoning steps"""
        return self.index.property_graph_store.query(cypher_query)
