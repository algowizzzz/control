#!/usr/bin/env python3
"""
sample_run.py: Demonstrate control-review agent usage scenarios
"""
from dotenv import load_dotenv
import os

# Construct explicit path to .env file in the project root
# __file__ is src/examples/sample_run.py
# os.path.dirname(__file__) is src/examples
# os.path.join(..., '..') is src/
# os.path.join(..., '..', '..') is project_root/
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
dotenv_path = os.path.join(project_root, '.env')

load_success = load_dotenv(dotenv_path=dotenv_path)
print(f"Attempting to load .env from: {dotenv_path}")
print(f".env file load success: {load_success}")

api_key_from_env = os.environ.get("ANTHROPIC_API_KEY")
if api_key_from_env:
    print("ANTHROPIC_API_KEY found in environment by sample_run.py.")
else:
    print("ANTHROPIC_API_KEY *NOT* found in environment by sample_run.py after explicit load_dotenv().")
    print(f"Current working directory: {os.getcwd()}")
    if not os.path.exists(dotenv_path):
        print(f"Explicitly checked path {dotenv_path} and it does NOT exist.")
    else:
        print(f"Explicitly checked path {dotenv_path} and it DOES exist. Check file content/permissions.")

from ..agent import agent 
from ..data_loader import filter_controls 
from ..prompts import get_prompt 

def print_header(title: str):
    print("\n" + "=" * len(title))
    print(title)
    print("=" * len(title) + "\n")

def main():
    # Scenario 1: Filter controls by control IDs
    print_header("Scenario 1: Filter by control IDs")
    control_ids_to_filter = ["CTRL1001", "CTRL1002", "CTRL1003"] 
    
    print(f"Attempting to filter for controls: {control_ids_to_filter}. Ensure they exist in controls.json.")
    
    initial_controls_for_demo = []
    for cid in control_ids_to_filter:
        matches = filter_controls({"control_id": cid})
        if matches:
            initial_controls_for_demo.append(matches[0])
        else:
            print(f"Warning: Control ID '{cid}' not found in controls.json.")

    if not initial_controls_for_demo:
        print("Error: No specified control IDs found. Populating with generic placeholders for demo continuation.")
        print("Please ensure your controls.json is populated and contains control_id fields.")
        initial_controls_for_demo = [
            {"control_id": "CTRL_PLACEHOLDER_1", "description": "This is a placeholder for demo purposes."},
            {"control_id": "CTRL_PLACEHOLDER_2", "description": "Another placeholder control."}
        ]
    
    print(f"Using the following controls for demo scenarios: {[c['control_id'] for c in initial_controls_for_demo]}")

    # Scenario 2: Single 5W review
    print_header("Scenario 2: Single 5W review")
    if initial_controls_for_demo:
        control_to_review_single = initial_controls_for_demo[0]
        print(f"5W for {control_to_review_single['control_id']}: \n", agent.run(
            f"Review control {control_to_review_single['control_id']} using 5W. Here is the control data: {control_to_review_single}"))
    else:
        print("Skipping Scenario 2: No controls available for review.")

    # Scenario 3: Batch review (5W, OE, DE)
    print_header("Scenario 3: Batch review")
    if len(initial_controls_for_demo) >= 1:
        batch_controls = initial_controls_for_demo[:min(2, len(initial_controls_for_demo))]
        ids_for_batch = ", ".join([c['control_id'] for c in batch_controls])
        batch_controls_data_list = [dict(c) for c in batch_controls]
        print(agent.run(
            f"Review controls with IDs {ids_for_batch} using 5W, OE, and DE. Here is the control data: {batch_controls_data_list}"))
    else:
        print("Skipping Scenario 3: Not enough controls for batch review.")

    # Scenario 4: Explain methods
    print_header("Scenario 4: Explain methods")
    print(agent.run("Explain how you perform 5W, OE, and DE analyses."))

    # Scenario 5: Self-awareness & introspection
    print_header("Scenario 5: Self-awareness queries")
    queries = [
        "What can you do?", "What data do you have access to?",
        "Who are you?", "How many tools do you have?",
        "List your tools and describe them.",
        "What is the current model name for the LLM?"
    ]
    for q in queries:
        print(f"> {q}\n", agent.run(q))

    # Scenario 6: Inspect current 5W prompt
    print_header("Scenario 6: Inspect 5W prompt")
    current_5w_prompt = get_prompt("5W")
    if current_5w_prompt:
        print(current_5w_prompt.template)
    else:
        print("Could not retrieve 5W prompt.")

    # Scenario 7: Modify 5W prompt & rerun
    print_header("Scenario 7: Modify 5W prompt & rerun")
    new_5w_template = (
        "You are an extremely thorough control-review expert. Perform an exhaustive 5W analysis "
        "(Who, What, Where, When, Why, and How - if applicable) for the provided control. "
        "Emphasize context, scope, impact, and evidence of operation:\n\nCONTROL DETAILS: {control}"
    )
    print(f"Attempting to update 5W prompt with new template:\n{new_5w_template}")
    escaped_template_string = new_5w_template.replace("'", "\\'")
    update_result = agent.run(f"Update the prompt for '5W' with the following template: '''{escaped_template_string}'''")
    print(f"Update result: {update_result}")

    print("\nInspecting 5W prompt after attempting update:")
    updated_5w_prompt = get_prompt("5W")
    if updated_5w_prompt:
        print(updated_5w_prompt.template)
    else:
        print("Could not retrieve 5W prompt after update attempt.")

    if initial_controls_for_demo and ("success" in update_result.lower() or "updated" in update_result.lower()):
        control_for_rerun = initial_controls_for_demo[0]
        print(f"\nRerunning 5W review for {control_for_rerun['control_id']} with the (hopefully) updated prompt:")
        print(agent.run(f"Review control {control_for_rerun['control_id']} using 5W. Control data: {control_for_rerun}"))
    elif not initial_controls_for_demo:
        print("Skipping rerun: no controls available.")
    else:
        print(f"Skipping rerun: prompt update may have failed. Agent response: {update_result}")

    # Scenario 8: Direct object review with explicit data
    print_header("Scenario 8: Direct object review with explicit data")
    if initial_controls_for_demo:
        direct_review_control = initial_controls_for_demo[0]
        print(agent.run(f"Review this control using 5W, OE, DE. The control data is: {direct_review_control}"))
    else:
        print("Skipping Scenario 8: No controls available for direct object review.")

    # Scenario 9: Review process & prompts
    print_header("Scenario 9: Review process & prompts")
    print(agent.run("How are the controls reviewed and what prompts are used?"))

if __name__ == "__main__":
    main() 