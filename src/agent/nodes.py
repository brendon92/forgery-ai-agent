from typing import Dict, Any
import json
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from src.agent.state import AgentState
from src.utils.config import config
from src.tools.tool_router import SemanticToolRouter

# Initialize LLM
from src.agent.model_factory import ModelFactory

# Remove global llm
# llm = ChatOpenAI(model="gpt-4o", api_key=config.OPENAI_API_KEY)

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
        
        # Get Reflector Model (usually kept as 'reflector' -> gpt-4o or similar strong model)
        # But user might want local strong model for pivot
        llm = ModelFactory.get_model("reflector")
        
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
        
        # Self-Improvement Logic:
        # If score is low, maybe we need a smarter model next time?
        # Update active_model_type for the subsequent retry in the Agent Node
        updates = {
            "reflection_score": score, 
            "retry_count": state.get("retry_count", 0) + 1
        }
        
        if score < 0.7:
             # Strategy: Switch to 'smart' or 'local_smart' if we were on 'fast'
             current_model = state.get("active_model_type", "fast")
             if current_model == "fast":
                 print("REFLECTION: Downgrading confidence, switching to SMART model for retry.")
                 updates["active_model_type"] = "smart" # or 'local_smart' depending on preference
                 
        return updates

def agent_node(state: AgentState):
    """
    The core agent node that generates a response based on the current state.
    Uses RAG-on-Tools to select relevant tools first.
    """
    messages = state['messages']
    user_query = messages[-1].content
    
    # Resolve Model
    model_type = state.get("active_model_type", "fast") # Default to fast (e.g. qwen)
    llm = ModelFactory.get_model(model_type)
    print(f"AGENT: Using model type '{model_type}' -> {getattr(llm, 'model', 'unknown')}")
    
    # Dynamic Tool Retrieval
    relevant_tools = tool_router.route(user_query)
    
    # If we have tools, bind them. Ideally we convert schemas to a format the LLM accepts.
    # For now, we'll just inject them into the system prompt as a lightweight approach
    # until we have full Pydantic models for every tool.
    # But to support function calling, we can use a generic "call_tool" binding or raw tool binding if possible.
    
    tools_context = ""
    if relevant_tools:
        tools_list = "\n".join([f"- {t['name']}: {t['description']}" for t in relevant_tools])
        tools_context = f"\nAVAILABLE TOOLS:\n{tools_list}\n\nTo use a tool, strictly output a JSON block: {{\"tool\": \"tool_name\", \"args\": {{...}}}}"

    # Use dynamic system instructions if available, otherwise fallback
    base_instructions = state.get("system_instructions")
    if not base_instructions:
        base_instructions = "You are Forgery, an expert executive AI assistant."

    system_prompt = (
        f"{base_instructions}\n"
        f"{tools_context}\n"
        "If you can answer directly, do so."
    )
    
    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    return {"messages": [response]}

import re
async def tool_node(state: AgentState):
    """
    Executes a tool call if the last message contains one.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    # Simple parsing logic for tool calls in text
    content = last_message.content
    
    # Regex to find JSON block
    # Matches ```json { ... } ``` or just { ... }
    # This is a basic implementation.
    json_match = re.search(r"\{.*\}", content, re.DOTALL)
    
    try:
        if json_match:
            tool_call = json.loads(json_match.group(0))
            if "tool" in tool_call:
                from src.tools.mcp_manager import mcp_manager
                
                tool_name = tool_call["tool"]
                args = tool_call.get("args", {})
                
                print(f"Executing tool: {tool_name}")
                
                server_name = None
                for s_name, conn in mcp_manager.connections.items():
                    if tool_name in conn["tools"]:
                        server_name = s_name
                        break
                
                if server_name:
                    # Async execution
                    try:
                        result = await mcp_manager.call_tool(server_name, tool_name, args)
                        return {"messages": [AIMessage(content=f"Tool Result: {result}")]}
                    except Exception as e:
                         return {"messages": [AIMessage(content=f"Error executing tool: {e}")]}
                else:
                    return {"messages": [AIMessage(content=f"Error: Tool '{tool_name}' not found on any connected MCP server.")]}
    except Exception as e:
        print(f"Tool execution parsing failed: {e}")

    return {"messages": [AIMessage(content="No tool executed. Proceeding.")]}
