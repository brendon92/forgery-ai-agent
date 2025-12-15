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
    user_query = messages[-1].content
    
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

    system_prompt = (
        "You are Forgery, an expert executive AI assistant. "
        f"{tools_context}"
        "\nIf you can answer directly, do so."
    )
    
    response = llm.invoke([SystemMessage(content=system_prompt)] + messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    """
    Executes tools by parsing the last message for tool calls.
    Connects to the MCP server to execute.
    """
    messages = state['messages']
    last_message = messages[-1]
    
    # Simple JSON parsing for tool calls (since we prompted for JSON)
    # In a more advanced setup with .bind_tools(), we would check message.tool_calls
    tool_content = last_message.content
    
    try:
        # Extract JSON if present
        import re
        json_match = re.search(r'\{.*\}', tool_content, re.DOTALL)
        if json_match:
            tool_call = json.loads(json_match.group(0))
            if "tool" in tool_call:
                from src.tools.mcp_client import mcp_client
                
                tool_name = tool_call["tool"]
                args = tool_call.get("args", {})
                
                print(f"Executing tool: {tool_name}")
                # Ideally async, but node is sync here unless we change to async def
                # For now using a sync wrapper or just simulating the call if client is async only
                # The mcp_client.call_tool is async. We need to run it.
                import asyncio
                result = asyncio.run(mcp_client.call_tool(tool_name, args))
                
                return {"messages": [AIMessage(content=f"Tool Result: {result}")]}
    except Exception as e:
        print(f"Tool execution parsing failed: {e}")

    return {"messages": [AIMessage(content="No tool executed. Proceeding.")]}
