from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uuid

router = APIRouter(prefix="/crews", tags=["crews"])

# In-memory storage for crews
crews_db: Dict[str, Dict] = {}

class CrewCreate(BaseModel):
    name: str
    description: str
    agent_ids: List[str]
    process: str = "sequential" # or 'hierarchical'

class CrewResponse(CrewCreate):
    id: str

@router.get("/", response_model=List[CrewResponse])
async def list_crews():
    return list(crews_db.values())

@router.post("/", response_model=CrewResponse)
async def create_crew(crew: CrewCreate):
    crew_id = str(uuid.uuid4())
    new_crew = crew.dict()
    new_crew["id"] = crew_id
    crews_db[crew_id] = new_crew
    return new_crew

@router.post("/{crew_id}/run")
async def run_crew(crew_id: str, task_description: str):
    if crew_id not in crews_db:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    # Future: Instantiate CrewAI runner here
    return {"status": "started", "job_id": str(uuid.uuid4()), "message": "Crew execution started (Simulation)"}
