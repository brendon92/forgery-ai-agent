import os
from typing import List, Optional
from llama_index.core import Document, PropertyGraphIndex
from llama_index.graph_stores.neo4j import Neo4jGraphStore
from llama_index.llms.openai import OpenAI
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor

from src.memory.graph_schema import NodeLabel, RelationshipType

class GraphIngestionPipeline:
    def __init__(self):
        # Initialize connection to Neo4j
        self.graph_store = Neo4jGraphStore(
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password"),
            url=os.getenv("NEO4J_URL", "bolt://localhost:7687"),
        )
        
        # Initialize Property Graph Index
        # We use SchemaLLMPathExtractor to extract entities aligned with our schema
        self.index = PropertyGraphIndex.from_existing(
            property_graph_store=self.graph_store,
            kg_extractors=[
                SchemaLLMPathExtractor(
                    llm=OpenAI(model="gpt-4"),
                    possible_entities=[e.value for e in NodeLabel],
                    possible_relations=[r.value for r in RelationshipType],
                    strict=False # Avoid Pydantic schema error
                )
            ]
        )

    async def ingest_documents(self, documents: List[Document], workspace_id: str):
        """
        Ingest a list of documents into the GraphRAG system.
        Tags nodes with workspace_id for isolation.
        """
        print(f"Ingesting {len(documents)} documents for workspace {workspace_id}...")
        
        # Add workspace_id metadata to all documents
        for doc in documents:
            doc.metadata["workspace_id"] = workspace_id

        self.index.insert_nodes(documents)
        
        # Post-processing: Link all nodes with this workspace_id to the Workspace node
        # This ensures that both extracted entities and source documents are connected to the workspace
        print("Linking nodes to Workspace...")
        
        # Query to link any node with matching workspace_id to the Workspace node
        # We exclude the Workspace node itself to avoid self-loops
        link_query = f"""
        MATCH (w:{NodeLabel.WORKSPACE.value} {{id: $workspace_id}})
        MATCH (n)
        WHERE n.workspace_id = $workspace_id AND elementId(n) <> elementId(w)
        MERGE (n)-[:{RelationshipType.BELONGS_TO.value}]->(w)
        """
        
        self.graph_store.query(link_query, params={"workspace_id": workspace_id})
        
        print(f"Ingestion and linking complete for workspace {workspace_id}.")

    def add_workspace_node(self, workspace_id: str, title: str):
        """Creates the root Workspace node manually"""
        query = f"""
        MERGE (w:{NodeLabel.WORKSPACE} {{id: $id}})
        SET w.title = $title
        """
        self.graph_store.query(query, params={"id": workspace_id, "title": title})
