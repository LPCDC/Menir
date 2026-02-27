import os
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Try to import openai, handle if not installed
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from .tools import query_narrative_graph, find_relevant_chunks

load_dotenv()

class NarrativeAgent:
    """
    An agent that uses OpenAI's GPT models to query the Menir narrative graph.
    It can translate natural language into Cypher queries or Vector searches.
    """
    
    def __init__(self, model: str = "gpt-4o"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        
        if OpenAI is None:
            raise ImportError("The 'openai' library is required. Please install it with 'pip install openai'.")
            
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.conversation_history: List[Dict[str, Any]] = []
        
        # System Prompt
        self.system_prompt = """You are the Menir Narrative Assistant, an expert on the 'Livro Débora' story graph.
Your goal is to answer questions about the narrative, characters, and structure by querying the database.

You have access to two tools:
1. `query_narrative_graph`: Use this for STRUCTURAL or FACTUAL questions. 
   - E.g. "Who is in Chapter 1?", "How many scenes are there?", "What places are connected to Caroline?"
   - The graph has nodes: Work, Chapter, ChapterVersion, Scene, Event, Character, Place.
   - Relationships include: :HAS_SCENE, :NEXT_SCENE, :APPEARS_IN, :OCCURS_IN, :SET_IN.
   - ALWAYS output valid Cypher. ensure you LIMIT results if many are expected.

2. `find_relevant_chunks`: Use this for THEMATIC, CONTENT, or TEXTUAL questions.
   - E.g. "What did they say about the 'wall'?", "Summarize the argument between X and Y."
   - This searches the vector database of text chunks.

STRATEGY:
- If the user asks for character lists, counts, or relationships -> Use Graph Query.
- If the user asks about what happened, specific quotes, or feelings -> Use Chunk Search.
- You can use BOTH if needed.

SAFETY:
- You are strictly READ-ONLY. Do not try to create or delete nodes.
"""

    def _get_tools_definition(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "query_narrative_graph",
                    "description": "Execute a Cypher query on the Neo4j narrative graph.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The Cypher query to execute. Must be read-only."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "find_relevant_chunks",
                    "description": "Search for relevant text chunks using semantic vector search.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query (natural language)."
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of chunks to retrieve (default 3).",
                                "default": 3
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    def chat(self, user_input: str) -> str:
        """
        Main interaction loop. Sends user input to LLM, handles tool calls, allows LLM to synthesize answer.
        """
        # Initialize conversation if empty
        if not self.conversation_history:
            self.conversation_history.append({"role": "system", "content": self.system_prompt})
            
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # First call to LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.conversation_history,
            tools=self._get_tools_definition(),
            tool_choice="auto"
        )
        
        message = response.choices[0].message
        
        # Check if the model wants to call a tool
        if message.tool_calls:
            self.conversation_history.append(message)  # Add the assistant's "thinking" (tool call request)
            
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                tool_output = None
                
                print(f"[Agent] Calling tool: {function_name}") # Debug output
                
                if function_name == "query_narrative_graph":
                    tool_output = query_narrative_graph(arguments["query"])
                elif function_name == "find_relevant_chunks":
                    top_k = arguments.get("top_k", 3)
                    tool_output = find_relevant_chunks(arguments["query"], top_k=top_k)
                
                # Append tool result to history
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(tool_output)
                })
            
            # Second call to LLM (with tool outputs)
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history
            )
            final_message = final_response.choices[0].message
            self.conversation_history.append(final_message)
            return final_message.content
            
        else:
            # parsing non-tool response
            self.conversation_history.append(message)
            return message.content

    def reset_history(self):
        self.conversation_history = []
