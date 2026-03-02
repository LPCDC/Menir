import sys
import os
import argparse
from menir_core.rag.agent import NarrativeAgent
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Menir Narrative Assistant (GraphRAG)")
    parser.add_argument("query", nargs="?", help="The question to ask Menir")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI Model to use")
    
    args = parser.parse_args()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment.")
        print("Please add it to your .env file.")
        sys.exit(1)
        
    try:
        agent = NarrativeAgent(model=args.model)
    except ImportError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Initialization Error: {e}")
        sys.exit(1)
        
    print(f"🤖 Menir RAG Agent initialized ({args.model})")
    
    if args.query:
        # Single shot
        print(f"\n👤 You: {args.query}")
        print("🤖 Menir: thinking...", end="\r")
        try:
            response = agent.chat(args.query)
            print(f"🤖 Menir: {response}")
        except Exception as e:
            print(f"\n❌ Error during chat: {e}")
    else:
        # Interactive mode
        print("\nEntering interactive mode. Type 'exit' to quit.\n")
        while True:
            try:
                user_input = input("👤 You: ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                if not user_input.strip():
                    continue
                
                print("🤖 Menir: thinking...", end="\r")
                response = agent.chat(user_input)
                # clear thinking line
                print(" " * 20, end="\r")
                print(f"🤖 Menir: {response}\n")
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
