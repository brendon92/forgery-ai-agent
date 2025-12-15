from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

# In a real app, we'd inject these dependencies
from src.memory.graph_ingestion import GraphIngestionPipeline
# from src.memory.graph_retrieval import GraphRetrievalSystem 

router = APIRouter(prefix="/workspaces", tags=["workspaces"])
ingestion_pipeline = GraphIngestionPipeline()

class WorkspaceCreate(BaseModel):
    title: str
    goal: Optional[str] = None

class WorkspaceResponse(BaseModel):
    id: str
    title: str
    goal: Optional[str]

@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(workspace: WorkspaceCreate):
    workspace_id = str(uuid.uuid4())
    # Create the root Workspace node in Neo4j
    try:
        ingestion_pipeline.add_workspace_node(workspace_id, workspace.title)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return {
        "id": workspace_id,
        "title": workspace.title,
        "goal": workspace.goal
    }

@router.post("/{workspace_id}/files")
async def upload_workspace_files(workspace_id: str, files: List[UploadFile] = File(...)):
    """
    Uploads files to a workspace and triggers the GraphRAG ingestion pipeline.
    """
    documents = []
    for file in files:
        content = await file.read()
        # Create a LlamaIndex Document
        # In prod, we'd use a proper parser (PDF/Docx) based on content_type
        from llama_index.core import Document
        doc = Document(
            text=content.decode("utf-8", errors="ignore"),
            metadata={"filename": file.filename}
        )
        documents.append(doc)
    
    # Trigger ingestion
    try:
        await ingestion_pipeline.ingest_documents(documents, workspace_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
        
    return {"status": "success", "processed_files": len(files)}

@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces():
    # In a real implementation effectively query Neo4j for all Workspace nodes
    # For now, we'll need a method in ingestion_pipeline or a direct query here
    # Since ingestion_pipeline wraps storage, let's assume we can query via driver
    try:
        results, _, _ = ingestion_pipeline.graph_store.query(
            f"MATCH (w:Workspace) RETURN w.id as id, w.title as title, w.goal as goal"
        )
        workspaces = []
        for record in results:
            # Assuming record is a list/dict depending on driver wrapper
            # Neo4j python driver returns Record objects
            workspaces.append({
                "id": record["id"],
                "title": record["title"],
                "goal": record.get("goal")
            })
        return workspaces
    except Exception as e:
        print(f"Error listing workspaces: {e}")
        return []

@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str):
    try:
        # Delete workspace and all its HAS_FILE relations and BELONGS_TO relations
        # We might want to cascade delete all nodes belonging to it if strict isolation
        query = """
        MATCH (w:Workspace {id: $workspace_id})
        DETACH DELETE w
        """
        ingestion_pipeline.graph_store.query(query, params={"workspace_id": workspace_id})
        
        # Also cleanup vector store for this workspace_id if we filtered by it
        # (Not implemented in this step, but noted)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{workspace_id}/files")
async def list_workspace_files(workspace_id: str):
    # This would require querying the graph for Document nodes linked to the Workspace
    # Not strictly implemented in ingestion yet (we store as raw nodes)
    # But if we did ingestion_pipeline.insert_nodes, they are in the graph store.
    return []

@router.get("/{workspace_id}/graph")
async def get_workspace_graph(workspace_id: str):
    """
    Export the sub-graph for visualization.
    Returns nodes and edges in a format suitable for visualizers.
    """
    query = """
    MATCH (w:Workspace {id: $workspace_id})-[r*1..2]-(n)
    RETURN w, r, n LIMIT 100
    """
    try:
        # We need to return raw graph data
        # Check if query method returns raw neo4j records
        data, keys, _ = ingestion_pipeline.graph_store.query(query, params={"workspace_id": workspace_id})
        
        # Transform to JSON structure
        nodes = []
        links = []
        seen_nodes = set()
        
        for record in data:
            # Parse record items
            pass 
        
        # Simplified return for now
        return {"nodes": [], "links": []} 
    except Exception as e:
        print(f"Graph query failed: {e}")
        return {"nodes": [], "links": []}
