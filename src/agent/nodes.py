from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from src.agent.state import AgentState
from src.utils.config import config

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o", api_key=config.OPENAI_API_KEY)

def agent_node(state: AgentState):
    """
    The core agent node that generates a response based on the current state.
    """
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

def reflection_node(state: AgentState):
    """
    Critiques the agent's response.
    """
    messages = state['messages']
    last_message = messages[-1]
    
    # Simple reflection logic for now
    reflection_prompt = f"Critique the following response: {last_message.content}. Return a score from 0.0 to 1.0."
    reflection = llm.invoke([HumanMessage(content=reflection_prompt)])
    
    # Mock parsing logic - in real impl we'd use structured output
    try:
        score = float(reflection.content.strip())
    except:
        score = 0.5 # Default fallback
        
    return {"reflection_score": score}

def tool_node(state: AgentState):
    """
    Executes tools. Mock implementation for now.
    """
    # In real impl, this would call the MCP client
    return {"messages": [AIMessage(content="Tool execution result placeholder")]}

def should_continue(state: AgentState):
    """
    Router logic.
    """
    if state['reflection_score'] > 0.8:
        return "end"
    if state['retry_count'] > 3:
        return "end"
    return "reflect"
