from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict
import os
import json

router = APIRouter(prefix="/settings", tags=["settings"])

CONFIG_FILE = "agent_config.json"

class AgentConfig(BaseModel):
    reflection_threshold: float = 0.8
    max_retries: int = 3
    system_prompt: str = "You are a helpful AI assistant."

class ApiKeys(BaseModel):
    openai_api_key: Optional[str] = None
    langfuse_public_key: Optional[str] = None
    langfuse_secret_key: Optional[str] = None
    qdrant_api_key: Optional[str] = None

class ModelSelection(BaseModel):
    llm_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    temperature: float = 0.7

class ServiceEndpoints(BaseModel):
    neo4j_uri: str = "bolt://localhost:7687"
    qdrant_url: str = "http://localhost:6333"
    langfuse_host: str = "http://localhost:3000"

class Settings(BaseModel):
    agent_config: AgentConfig
    api_keys: ApiKeys
    model_selection: ModelSelection
    service_endpoints: ServiceEndpoints

    @validator("api_keys")
    def validate_keys(cls, v):
        if v.openai_api_key and not v.openai_api_key.startswith("sk-"):
            raise ValueError("Invalid OpenAI API Key format")
        return v

# Default configuration
default_settings = Settings(
    agent_config=AgentConfig(),
    api_keys=ApiKeys(),
    model_selection=ModelSelection(),
    service_endpoints=ServiceEndpoints()
)

def load_settings() -> Settings:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                return Settings(**data)
        except Exception as e:
            print(f"Error loading config: {e}")
    return default_settings

def save_settings(settings: Settings):
    with open(CONFIG_FILE, "w") as f:
        f.write(settings.json(indent=2))

@router.get("/", response_model=Settings)
async def get_settings():
    return load_settings()

@router.put("/", response_model=Settings)
async def update_settings(settings: Settings):
    try:
        # Save to file
        save_settings(settings)
        
        # In a real app, we might need to reload global config or notify services
        # e.g., update os.environ for immediate effect in some modules
        if settings.api_keys.openai_api_key:
            os.environ["OPENAI_API_KEY"] = settings.api_keys.openai_api_key
            
        return settings
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
