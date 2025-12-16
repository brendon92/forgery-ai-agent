from typing import TypedDict, Annotated, List, Union
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_step: str
    reflection_score: float
    retry_count: int
    agent_id: str
    system_instructions: str
    active_model_type: str # 'fast', 'smart', 'local_smart'
