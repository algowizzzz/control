import os
import sys
from dotenv import load_dotenv
import datetime

# Ensure the src directory is in the Python path
# This allows us to import modules from the src directory as a package
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "..")) # Go up one level to /src
project_root = os.path.abspath(os.path.join(src_dir, "..")) # Go up another level to project root

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if project_root not in sys.path: # To find .env at project root
    sys.path.insert(0, project_root)

# --- Load Environment Variables ---
# Attempt to load .env file from the project root
dotenv_path = os.path.join(project_root, ".env")
print(f"Attempting to load .env from: {dotenv_path}")
load_success = load_dotenv(dotenv_path=dotenv_path, verbose=True)
print(f".env file load success: {load_success}")

api_key_present = bool(os.environ.get("ANTHROPIC_API_KEY"))
if not api_key_present:
    print("ANTHROPIC_API_KEY *NOT* found in environment by real_data_run.py after explicit load_dotenv().")
    # Check current working directory and if .env exists there, for debugging
    print(f"Current working directory: {os.getcwd()}")
    local_dotenv_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(local_dotenv_path):
        print(f"Explicitly checked path {local_dotenv_path} and it DOES exist. Check file content/permissions.")
    else:
        print(f"Explicitly checked path {local_dotenv_path} and it does NOT exist.")
else:
    print("ANTHROPIC_API_KEY found in environment by real_data_run.py.")


# --- Import Agent ---
# Now that sys.path is set, we can import the agent
import agent

# --- Sample "Real" Control Data ---
REAL_CONTROLS_DATA = [
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
    },
    {
        "control_id": "BCP-002",
        "description": "A comprehensive business continuity plan (BCP) and disaster recovery (DR) plan is maintained and tested annually.",
        "owner": "Business Continuity Team",
        "category": "Business Continuity Planning",
        "objective": "To ensure the organization can recover critical business functions and IT systems in the event of a significant disruption.",
        "status": "Active",
        "last_reviewed_date": "2023-11-20",
        "review_frequency": "Annually"
    }
]

def main():
    print("--- Starting Real Data Control Review Agent Scenarios ---")

    # Prepare output file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(current_dir, f"real_data_run_output_{timestamp}.txt")
    with open(output_path, "w") as f:
        f.write(f"Real Data Control Review Agent Run - {timestamp}\n\n")

        # Scenario 1: Single 5W review on a real control
        print("\n=======================================")
        print("Scenario 1: Single 5W review (Real Data)")
        print("=======================================\n")
        if REAL_CONTROLS_DATA:
            control_to_review_single = REAL_CONTROLS_DATA[0]
            query1 = f"Review control {control_to_review_single['control_id']} using 5W. Here is the control data: {control_to_review_single}"
            print(f"Reviewing control: {control_to_review_single['control_id']}\n")
            try:
                response1 = agent.agent.run(query1)
                print(f"5W for {control_to_review_single['control_id']}: \n{response1}\n")
                f.write("--- Scenario 1: Single 5W Review ---\n")
                f.write(f"Query:\n{query1}\n\nResponse:\n{response1}\n\n")
            except Exception as e:
                print(f"Error during single 5W review (Real Data): {e}")
                f.write(f"Error during single 5W review: {e}\n\n")
        else:
            print("No real controls data to run Scenario 1.")
            f.write("No real controls data to run Scenario 1.\n\n")

        # Scenario 2: Batch review (5W, OE, DE) on real controls
        print("\n===================================================")
        print("Scenario 2: Batch review (5W, OE, DE) (Real Data)")
        print("===================================================\n")
        if len(REAL_CONTROLS_DATA) >= 2:
            controls_for_batch = REAL_CONTROLS_DATA[:2]
            ids_for_batch = [c['control_id'] for c in controls_for_batch]
            query2 = f"Review controls with IDs {ids_for_batch} using 5W, OE, and DE. Here is the control data: {controls_for_batch}"
            print(f"Reviewing controls: {ids_for_batch}\n")
            try:
                response2 = agent.agent.run(query2)
                print(f"Batch review for {ids_for_batch}: \n{response2}\n")
                f.write("--- Scenario 2: Batch Review (5W, OE, DE) ---\n")
                f.write(f"Query:\n{query2}\n\nResponse:\n{response2}\n\n")
            except Exception as e:
                print(f"Error during batch review (Real Data): {e}")
                f.write(f"Error during batch review: {e}\n\n")
        else:
            print("Not enough real controls data to run Scenario 2 (need at least 2).")
            f.write("Not enough real controls data to run Scenario 2 (need at least 2).\n\n")
        
        print(f"\n--- Real Data Control Review Agent Scenarios Complete ---\nOutput saved to: {output_path}\n")

if __name__ == "__main__":
    main() 