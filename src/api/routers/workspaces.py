from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
from neo4j import GraphDatabase
from src.utils.config import config

# In a real app, we'd inject these dependencies
from src.memory.graph_ingestion import GraphIngestionPipeline
# from src.memory.graph_retrieval import GraphRetrievalSystem 

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

# Lazy instantiation to prevent import-time connection errors
_ingestion_pipeline = None

def get_ingestion_pipeline():
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        _ingestion_pipeline = GraphIngestionPipeline()
    return _ingestion_pipeline

def get_db_driver():
    return GraphDatabase.driver(
        config.NEO4J_URI, 
        auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD)
    )

class WorkspaceCreate(BaseModel):
    title: str
    goal: Optional[str] = None

class WorkspaceResponse(BaseModel):
    id: str
    title: str
    goal: Optional[str]

class FileNodeResponse(BaseModel):
    id: str
    name: str
    type: str = "file"

@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(workspace: WorkspaceCreate):
    workspace_id = str(uuid.uuid4())
    # Create the root Workspace node in Neo4j
    try:
        pipeline = get_ingestion_pipeline()
        pipeline.add_workspace_node(workspace_id, workspace.title, workspace.goal)
    except Exception as e:
        print(f"Error creating workspace: {e}")
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
    Saves raw files to disk for hybrid memory strategy.
    """
    import os
    import aiofiles
    
    # Ensure directory exists
    raw_dir = f"data/workspaces/{workspace_id}/raw"
    os.makedirs(raw_dir, exist_ok=True)

    documents = []
    for file in files:
        # Save raw file
        file_path = os.path.join(raw_dir, file.filename)
        content = await file.read()
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            await out_file.write(content)
            
        # Create a LlamaIndex Document from the content
        # In prod, we'd use a proper parser (PDF/Docx) based on content_type
        # For now we duplicate logic to ensure we can create a File node easily if the pipeline doesn't
        # But let's stick to the pipeline
        from llama_index.core import Document
        doc = Document(
            text=content.decode("utf-8", errors="ignore"),
            metadata={"filename": file.filename, "file_path": file_path}
        )
        documents.append(doc)
    
    # Trigger ingestion
    try:
        pipeline = get_ingestion_pipeline()
        await pipeline.ingest_documents(documents, workspace_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
        
    return {"status": "success", "processed_files": len(files)}

@router.get("/", response_model=List[WorkspaceResponse])
async def list_workspaces():
    driver = get_db_driver()
    try:
        query = "MATCH (w:Workspace) RETURN w"
        with driver.session() as session:
            results = session.run(query)
            workspaces = []
            for record in results:
                node = record["w"]
                workspaces.append({
                    "id": node.get("id"),
                    "title": node.get("title"),
                    "goal": node.get("goal")
                })
            return workspaces
    except Exception as e:
        print(f"Error listing workspaces: {e}")
        return []
    finally:
        driver.close()

@router.delete("/{workspace_id}")
async def delete_workspace(workspace_id: str):
    driver = get_db_driver()
    try:
        # Delete workspace and all its HAS_FILE relations and BELONGS_TO relations
        query = """
        MATCH (w:Workspace {id: $workspace_id})
        DETACH DELETE w
        """
        with driver.session() as session:
            session.run(query, workspace_id=workspace_id)
        
        # Also cleanup vector store for this workspace_id if we filtered by it
        # (Not implemented in this step, but noted)
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.close()

@router.get("/{workspace_id}/files", response_model=List[FileNodeResponse])
async def list_workspace_files(workspace_id: str):
    driver = get_db_driver()
    try:
        # Find Document nodes connected to the workspace
        # Assuming the ingestion pipeline creates (Workspace)-[:HAS_DOCUMENT]->(Document)
        # or (Document)-[:BELONGS_TO]->(Workspace). 
        # Checking LlamaIndex PropertyGraph default usually links chunks to docs.
        # We need to verify how `add_workspace_node` and `ingest_documents` work in `graph_ingestion.py`
        # But for now assuming a generic relation exists or we search for nodes with workspace_id metadata
        
        # Let's assume a standard pattern: (w:Workspace)-[:HAS_FILE]->(f:File) or similar
        # If not, we might settle for querying nodes with specific label and property.
        
        query = """
        MATCH (w:Workspace {id: $workspace_id})-->(n:Document) 
        RETURN n
        """
        # If exact relation is unknown, we might try:
        # MATCH (n:Document) WHERE n.workspace_id = $workspace_id
        
        with driver.session() as session:
            results = session.run(query, workspace_id=workspace_id)
            files = []
            for record in results:
                node = record["n"]
                files.append({
                    "id": node.get("id", str(uuid.uuid4())),
                    "name": node.get("file_name") or node.get("filename") or "Untitled",
                    "type": "file"
                })
            return files
    except Exception as e:
        print(f"Error listing files: {e}")
        return []
    finally:
        driver.close()

@router.get("/{workspace_id}/graph")
async def get_workspace_graph(workspace_id: str):
    """
    Export the sub-graph for visualization.
    Returns nodes and edges in a format suitable for visualizers.
    """
    driver = get_db_driver()
    query = """
    MATCH path = (w:Workspace {id: $workspace_id})-[*1..2]-(n)
    RETURN path LIMIT 100
    """
    try:
        with driver.session() as session:
            result = session.run(query, workspace_id=workspace_id)
            
            # Use sets to avoid duplicates
            nodes_dict = {}
            links_list = []
            
            for record in result:
                path = record["path"]
                for node in path.nodes:
                    nodes_dict[node.element_id] = {
                        "id": node.element_id, # internal ID for visualization
                        "labels": list(node.labels),
                        "properties": dict(node)
                    }
                for rel in path.relationships:
                    links_list.append({
                        "source": rel.start_node.element_id,
                        "target": rel.end_node.element_id,
                        "type": rel.type,
                        "properties": dict(rel)
                    })
            
            return {
                "nodes": list(nodes_dict.values()),
                "links": links_list
            }
    except Exception as e:
        print(f"Graph query failed: {e}")
        return {"nodes": [], "links": []}
    finally:
        driver.close()
