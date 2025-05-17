import os
import sys
from dotenv import load_dotenv

# Ensure the src directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "..")) # Go up one level to /src
project_root = os.path.abspath(os.path.join(src_dir, "..")) # Go up another level to project root

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path: # To find .env at project root
    sys.path.insert(0, project_root)

# --- Load Environment Variables ---
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path=dotenv_path, verbose=True)

# --- Import Agent ---
try:
    from ..agent import agent # Relative import for when run as a module
except ImportError:
    # Fallback for direct execution if needed, though module execution is preferred
    from agent import agent 

# --- Sample "Real" Control Data (can be used in your prompts if desired) ---
REAL_CONTROLS_DATA_EXAMPLES = [
    {
        "control_id": "ACC-001",
        "description": "User access reviews are performed quarterly for all critical financial systems.",
        "owner": "IT Security Team",
        "category": "Access Control",
        "objective": "To ensure only authorized personnel have access to critical financial systems and that access is revoked promptly upon termination or role change.",
        "status": "Active",
        "last_reviewed_date": "2024-03-15",
        "review_frequency": "Quarterly"
    },
    {
        "control_id": "CHG-005",
        "description": "All changes to production systems, including configurations, code, and infrastructure, must follow the documented change management process.",
        "owner": "Change Advisory Board (CAB)",
        "category": "Change Management",
        "objective": "To ensure that changes to production systems are properly authorized, tested, and implemented to minimize risk and disruption.",
        "status": "Active",
        "last_reviewed_date": "2024-04-02",
        "review_frequency": "Annually"
    }
]

def interactive_chat():
    print("--- Control Review Agent Interactive Chat ---")
    print("Type 'exit' or 'quit' to end the session.")
    print(f"Example control data you can reference (copy/paste into your prompt if needed):\n{REAL_CONTROLS_DATA_EXAMPLES[0]}\n")

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting chat.")
                break
            
            if not user_input.strip():
                continue

            print("Agent thinking...")
            response = agent.run(user_input)
            print(f"\nAgent: {response}")

        except KeyboardInterrupt:
            print("\nExiting chat due to interrupt.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            # Optionally, decide if you want to break the loop on error
            # break 

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("CRITICAL: ANTHROPIC_API_KEY not found in environment. The agent will not work.")
        print("Please ensure your .env file is correctly set up in the project root.")
    else:
        interactive_chat() 