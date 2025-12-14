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

@router.get("/{workspace_id}/graph")
async def get_workspace_graph(workspace_id: str):
    """
    Export the sub-graph for visualization.
    Simplified: Returns a cypher query result.
    """
    query = """
    MATCH (w:Workspace {id: $workspace_id})-[r*1..2]-(n)
    RETURN w, r, n LIMIT 100
    """
    # Assuming the driver or helper supports params, which LlamaIndex property graph usually does via run/query
    # But wait, self.graph_store.query usually takes params.
    # Let's check how it's called. The code below likely calls self.graph_store.client.query or similar.
    # If it's the LlamaIndex wrapper, we pass params differently.
    # Let's verify the call site first.
    # result = ingestion_pipeline.graph_store.query(query)
    # return result
    return {"message": "Graph export not fully implemented yet"}
