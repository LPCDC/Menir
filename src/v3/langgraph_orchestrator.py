import logging
from typing import Dict, Any, TypedDict, Annotated, List, Optional
import operator

# Configure logging
logger = logging.getLogger("LangGraphOrchestrator")
logger.setLevel(logging.INFO)

# Import our ContextVar to securely pass tenant_id
from src.v3.tenant_middleware import current_tenant_id

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.sqlite import SqliteSaver
    from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
    import sqlite3
    
    # Initialize the eternal memory DB
    conn = sqlite3.connect("memories.sqlite", check_same_thread=False)
    memory_saver = SqliteSaver(conn)
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("langgraph or langchain-core not found. Mocking structures for demonstration.")
    StateGraph = type("StateGraph", (), {"compile": lambda self, checkpointer=None: None, "add_node": lambda self, *a, **k: None, "set_entry_point": lambda self, *a: None, "add_edge": lambda self, *a: None, "add_conditional_edges": lambda self, *a: None})
    END = "END"
    memory_saver = None
    class BaseMessage: pass
    class HumanMessage(BaseMessage): 
        def __init__(self, content): self.content = content
    class AIMessage(BaseMessage): pass


# 1. Define the Graph State
class MenirState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    tenant_id: str
    thread_id: str
    memory: Dict[str, Any]
    error: Optional[str]

# 2. Node Functions
def context_injector_node(state: MenirState) -> Dict[str, Any]:
    """Node responsível por injetar o tenant_id no ContextVar imutável e seguro da thread corrente."""
    tenant = state.get("tenant_id")
    if not tenant:
        raise ValueError("Critical Security Error: tenant_id missing from state.")
        
    current_tenant_id.set(tenant)
    logger.info(f"🛡️ [Context Injector] Secured thread for tenant: {tenant}")
    
    return {"error": None}


def processing_node(state: MenirState) -> Dict[str, Any]:
    """Simula o agente LLM raciocinando e tentando acessar o Neo4j."""
    logger.info(f"🧠 [Processing Agent] Analyzing request for {state['tenant_id']}...")
    messages = state.get("messages", [])
    
    # In a real scenario, LLM would be invoked here.
    new_message = "Processed context securely."
    
    # We simulate a Cypher attempt if needed
    # If the LLM generates a bad query, an error could be produced here
    # leading back to a 'Reflect' node dynamically.
    
    return {"messages": [AIMessage(content=new_message)]}


def reflection_node(state: MenirState) -> Dict[str, Any]:
    """Node that evaluates errors (e.g. Neo4j SyntaxError) and rewrites the query."""
    err = state.get("error")
    if err:
        logger.warning(f"🔄 [Reflection] Agent repairing syntax error: {err}")
    return {"error": None}


# Routing Function
def route_after_processing(state: MenirState) -> str:
    if state.get("error"):
        return "reflect"
    return "end"


# 3. Build the State Graph
def build_menir_graph():
    graph_builder = StateGraph(MenirState)
    
    # Add Nodes
    graph_builder.add_node("inject_context", context_injector_node)
    graph_builder.add_node("process", processing_node)
    graph_builder.add_node("reflect", reflection_node)
    
    # Edges
    graph_builder.set_entry_point("inject_context")
    graph_builder.add_edge("inject_context", "process")
    
    graph_builder.add_conditional_edges(
        "process",
        route_after_processing,
        {"reflect": "reflect", "end": END}
    )
    
    # reflection loop back
    graph_builder.add_edge("reflect", "process")
    
    # Compile
    return graph_builder.compile(checkpointer=memory_saver)

# Instantiator exports
menir_graph = build_menir_graph()

if __name__ == "__main__":
    if LANGGRAPH_AVAILABLE:
        # Quick CLI Test
        initial_state = {
            "messages": [HumanMessage(content="Qual o status do meu projeto?")],
            "tenant_id": "PROJECT_ITAU_15220012",
            "thread_id": "thread_abc123",
            "memory": {},
            "error": None
        }
        
        logger.info("Starting run...")
        final_state = menir_graph.invoke(initial_state)
        logger.info(f"Run finished: {final_state}")
    else:
        print("LangGraph module unavailable. Dry-run mock loaded.")
