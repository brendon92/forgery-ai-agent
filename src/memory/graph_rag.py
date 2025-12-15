import os
from typing import List, Dict, Any
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from neo4j import GraphDatabase

class HybridGraphRAG:
    """
    Implements the Hybrid GraphRAG architecture:
    1. Knowledge Graph Traversal (Contextual Anchoring)
    2. Vector Search (Semantic Augmentation)
    """
    def __init__(self):
        # Neo4j Connection
        self.neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_auth = (os.getenv("NEO4J_USERNAME", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))
        self.driver = GraphDatabase.driver(self.neo4j_uri, auth=self.neo4j_auth)
        
        # Qdrant / Vector Store
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        try:
            self.vector_store = Qdrant.from_existing_collection(
                embedding=self.embeddings,
                collection_name="workspace_docs", # Assumed collection name
                url=os.getenv("QDRANT_URL", "http://localhost:6333"),
                api_key=os.getenv("QDRANT_API_KEY")
            )
        except:
             # Fallback or init later
             self.vector_store = None

    def query(self, user_query: str, workspace_id: str, depth: int = 2) -> str:
        """
        Executes the Hybrid RAG pipeline.
        Returns a rich context string for the LLM.
        """
        print(f"Executing GraphRAG for query: '{user_query}' in workspace {workspace_id}")
        
        # Step 1: Extract Entities (Simplified for now, use LLM in prod)
        # We assume the query contains keywords that match node names or properties
        # Ideally, use an EntityExtractionChain here.
        
        # Step 2: Graph Traversal
        # Traverse from workspace to find relevant connected nodes
        # This is a broad traversal; in prod, anchor to specific entities found in query
        cypher_query = f"""
        MATCH (w:Workspace {{id: $workspace_id}})-[:BELONGS_TO*1..{depth}]-(n)
        WHERE n.text IS NOT NULL # Assuming nodes have text properties or are chunks
        RETURN n.text as content, elementId(n) as id LIMIT 20
        """
        
        graph_context = []
        try:
            records, _, _ = self.driver.execute_query(cypher_query, workspace_id=workspace_id)
            for record in records:
                graph_context.append(record["content"])
        except Exception as e:
            print(f"Graph traversal failed: {e}")
            
        print(f"Graph Traversal found {len(graph_context)} nodes.")

        # Step 3: Vector Search (Guidance)
        # We can use the graph results to filter or re-rank, but standard RAG does parallel retrieval.
        # Here we perform a standard semantic search scoped to the workspace (if metadata available)
        vector_context = []
        if self.vector_store:
            try:
                # Filter by workspace_id metadata if possible (Qdrant supports filtering)
                # For now using pure semantic search
                results = self.vector_store.similarity_search(user_query, k=5)
                for doc in results:
                    # Check metadata if we implemented filtering
                    if doc.metadata.get("workspace_id") == workspace_id:
                        vector_context.append(doc.page_content)
            except Exception as e:
                print(f"Vector search failed: {e}")

        # Step 4: Synthesis
        # Combine unique contents
        unique_content = list(set(graph_context + vector_context))
        
        context_str = "\n---\n".join(unique_content)
        return context_str

    def close(self):
        self.driver.close()

graph_rag = HybridGraphRAG()
