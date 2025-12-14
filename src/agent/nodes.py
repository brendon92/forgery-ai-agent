from typing import Dict, Any
import json
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from src.agent.state import AgentState
from src.utils.config import config
from src.tools.tool_router import SemanticToolRouter

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", api_key=config.OPENAI_API_KEY)

# Initialize Router
tool_router = SemanticToolRouter(top_k=5)

class ReflectionNode:
    """
    Evaluates the agent's response against quality criteria.
    Criteria: Factual Grounding, JSON Schema compliance, Completeness.
    """
    def __call__(self, state: AgentState) -> Dict[str, Any]:
        messages = state['messages']
        last_message = messages[-1]
        
        # System prompt for the reflector
        system_prompt = (
            "You are a strict QA auditor for an AI agent. "
            "Evaluate the following response based on: "
            "1. Factual Grounding (is it hallucinatory?) "
            "2. Completeness (did it answer the user query?) "
            "3. Safety "
            "Return a JSON object: {\"score\": float (0.0-1.0), \"reason\": \"string\"}"
        )
        
        reflection_response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User Query: {messages[0].content}\nAgent Response: {last_message.content}")
        ])
        
        try:
            # Clean generic markdown blocks if present
            content = reflection_response.content.replace("```json", "").replace("```", "").strip()
            data = json.loads(content)
            score = float(data.get("score", 0.0))
            reason = data.get("reason", "No reason provided")
        except Exception as e:
            print(f"Reflection parsing failed: {e}")
            score = 0.5
            reason = "Parsing Error"
            
        print(f"Reflection Score: {score} | Reason: {reason}")
        
        return {
            "reflection_score": score, 
            "retry_count": state.get("retry_count", 0) + 1
        }

def agent_node(state: AgentState):
    """
    The core agent node that generates a response based on the current state.
    Uses RAG-on-Tools to select relevant tools first.
    """
    messages = state['messages']
    # Use the last human message or just the last message as context
    user_query = messages[-1].content
    
    # Dynamic Tool Retrieval
    relevant_tools = tool_router.route(user_query)
    
    # Construct a system message with tool definitions
    tools_context = "\n".join([f"- {t['name']}: {t['description']}" for t in relevant_tools])
    system_prompt = (
        "You are Forgery, an expert executive AI assistant. "
        "You have access to the following relevant tools:\n"
        f"{tools_context}\n"
        "If you need to use a tool, specify it clearly."
    )
    
    # In a real implementation, we would bind these tools to the LLM
    # llm_with_tools = llm.bind_structure(relevant_tools)
    
    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    """
    Executes tools.
    """
    # This needs to parse the LLM output and call the actual tool
    # For now, we simulate execution
    return {"messages": [AIMessage(content="Tool executed successfully.")]}
