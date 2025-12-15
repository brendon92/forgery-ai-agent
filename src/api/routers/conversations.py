from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime

router = APIRouter(prefix="", tags=["conversations"])

# In-memory storage for now (replace with DB later)
conversations_db: Dict[str, Dict[str, Any]] = {}
messages_db: Dict[str, List[Dict[str, Any]]] = {}

class ConversationCreate(BaseModel):
    title: str

class MessageCreate(BaseModel):
    role: str
    content: str

class ConversationResponse(BaseModel):
    id: str
    workspace_id: str
    title: str
    created_at: str
    updated_at: str

class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str

@router.post("/workspaces/{workspace_id}/conversations", response_model=ConversationResponse)
async def create_conversation(workspace_id: str, conversation: ConversationCreate):
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    new_conversation = {
        "id": conv_id,
        "workspace_id": workspace_id,
        "title": conversation.title,
        "created_at": now,
        "updated_at": now
    }
    
    conversations_db[conv_id] = new_conversation
    messages_db[conv_id] = []
    
    return new_conversation

@router.get("/workspaces/{workspace_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations(workspace_id: str):
    return [c for c in conversations_db.values() if c["workspace_id"] == workspace_id]

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversations_db[conversation_id]

@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(conversation_id: str, message: MessageCreate):
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    msg_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    new_message = {
        "id": msg_id,
        "role": message.role,
        "content": message.content,
        "timestamp": now
    }
    
    messages_db[conversation_id].append(new_message)
    
    # Update conversation timestamp
    conversations_db[conversation_id]["updated_at"] = now
    
    return new_message

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(conversation_id: str):
    if conversation_id not in conversations_db:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return messages_db.get(conversation_id, [])
