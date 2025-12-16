import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NEO4J_URI = os.getenv("NEO4J_URI", os.getenv("NEO4J_URL", "bolt://localhost:7687"))
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Local LLM / Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    
    # Model Configuration
    # Maps logical roles to physical model names
    MODEL_CONFIG = {
        "fast": "qwen2.5:1.5b",      # Fast, cheap, good for simple tasks
        "smart": "gpt-4o",           # The heavy lifter
        "local_smart": "llama3.2",   # Strongest local model
        "reflector": "gpt-4o",       # Self-correction usually needs high intelligence
    }

config = Config()
