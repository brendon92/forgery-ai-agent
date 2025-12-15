from langgraph.graph import StateGraph, END
from src.agent.state import AgentState
from src.agent.nodes import agent_node, ReflectionNode, tool_node

# Instantiate class-based nodes
reflection_node = ReflectionNode()

def route_agent_output(state: AgentState):
    """
    Determines if the agent is calling a tool or producing a final answer.
    """
    messages = state['messages']
    last_message = messages[-1]
    content = last_message.content
    
    # Check for JSON tool call pattern
    import re
    if re.search(r'\{.*"tool":.*\}', content, re.DOTALL):
        return "tools"
    return "reflect"

def should_continue(state: AgentState):
    """
    Router logic based on reflection score and retry count.
    """
    score = state.get('reflection_score', 0.0)
    retries = state.get('retry_count', 0)
    
    if score >= 0.8:
        print("Reflection Passed. Ending.")
        return "end"
    if retries >= 3: # Max 3 retries (total 4 attempts)
        print("Max retries reached. Ending.")
        return "end" # Or redirect to a 'failure' node
    
    print("Reflection Failed. Retrying.")
    return "agent"

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("reflect", reflection_node)
workflow.add_node("tools", tool_node)

# Set entry point
workflow.set_entry_point("agent")

# Add edges
workflow.add_edge("tools", "agent")

# Conditional Edges
# 1. From Agent -> Tools OR Reflect
workflow.add_conditional_edges(
    "agent",
    route_agent_output,
    {
        "tools": "tools",
        "reflect": "reflect"
    }
)

# 2. From Reflect -> End OR Agent (Loop)
workflow.add_conditional_edges(
    "reflect",
    should_continue,
    {
        "end": END,
        "agent": "agent"
    }
)

# Loop back from reflection to agent (Refinement Loop)
# In a real implementation, we might want a specific 'refine' node that
# takes the critique and modifies the original query
workflow.add_edge("reflect", "agent")

# Compile the graph
app = workflow.compile()
