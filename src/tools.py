from langchain.tools import Tool, tool
from langchain.chains import LLMChain
from langchain_anthropic import ChatAnthropic
from .data_loader import filter_controls as actual_filter_controls
from . import prompts
import os
import json

# Claude client setup - now configurable via environment variables
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL_NAME = os.environ.get("ANTHROPIC_MODEL_NAME", "claude-3-haiku-20240307")
TEMPERATURE = float(os.environ.get("ANTHROPIC_TEMPERATURE", 0.2))
MAX_TOKENS = int(os.environ.get("ANTHROPIC_MAX_TOKENS", 4096))

if not ANTHROPIC_API_KEY:
    print("Warning: ANTHROPIC_API_KEY not found in environment. LLM calls will likely fail.")

llm = ChatAnthropic(
    api_key=ANTHROPIC_API_KEY, 
    model=MODEL_NAME, 
    temperature=TEMPERATURE, 
    max_tokens=MAX_TOKENS
)

# Chains for analyses - using prompts from the prompts module
# These chains will have their .prompt attribute updated by the UpdatePromptTool
chain_5w = LLMChain(llm=llm, prompt=prompts.prompt_5w)
chain_oe = LLMChain(llm=llm, prompt=prompts.prompt_oe)
chain_de = LLMChain(llm=llm, prompt=prompts.prompt_de)
chain_methods = LLMChain(llm=llm, prompt=prompts.prompt_methods)

# Store chains in a dictionary to easily access them by key in the update tool
ANALYSIS_CHAINS = {
    "5W": chain_5w,
    "OE": chain_oe,
    "DE": chain_de,
    "METHODS": chain_methods # Though unlikely to be updated often
}

# Wrapper function for the FilterControls tool
def filter_controls_tool_func(input_str: str) -> list[dict[str, any]]:
    try:
        # Attempt to parse the input as JSON
        data = json.loads(input_str)
        if isinstance(data, dict):
            if 'control_id' in data:
                raw_ids = data['control_id']
                if isinstance(raw_ids, str):
                    return actual_filter_controls(control_ids=[raw_ids])
                elif isinstance(raw_ids, list):
                    # Ensure all items in the list are strings
                    if all(isinstance(item, str) for item in raw_ids):
                        return actual_filter_controls(control_ids=raw_ids)
                    else:
                        return [{"error": "Invalid item type in control_id list. All IDs must be strings."}]
                else:
                    return [{"error": "Invalid format for 'control_id' value in JSON input. Must be a string or list of strings."}]
            else:
                # Assume it's a filters dictionary
                return actual_filter_controls(filters=data)
        # If LLM provides a list of strings directly (e.g. ["ID1", "ID2"])
        elif isinstance(data, list) and all(isinstance(item, str) for item in data):
             return actual_filter_controls(control_ids=data)
        else:
            return [{"error": f"Parsed JSON input is not a dictionary of filters, a dictionary with 'control_id', or a list of ID strings: {input_str}"}]
    except json.JSONDecodeError:
        # Not a JSON string, assume it's a single control_id string directly
        return actual_filter_controls(control_ids=[input_str])
    except Exception as e:
        # Catch any other unexpected errors during parsing or filtering
        return [{"error": f"Error processing filter input: {str(e)}"}]

# Tool: Filter controls
filter_tool = Tool(
    name="FilterControls",
    func=filter_controls_tool_func, # Use the new wrapper function
    description='Filter controls by any attribute (e.g. {"category": "Access Control"}) or by control_id (e.g. "ACC-001" or {"control_id": "ACC-001"} or {"control_id": ["ACC-001", "ACC-002"]}). Returns a list of matching control objects.'
)

# Single-review helper
def single_review(control: dict, review_type: str) -> str:
    if review_type == "5W":
        # The chain_5w.prompt is now updated by UpdatePromptTool
        return chain_5w.run(control=control)
    if review_type == "OE":
        return chain_oe.run(control=control)
    if review_type == "DE":
        return chain_de.run(control=control)
    raise ValueError(f"Unknown review type: {review_type}")

# Batch-review tool with 10-control cap
def batch_review_func(tool_input_str: str) -> dict[str, dict[str, str]]:
    try:
        tool_input = json.loads(tool_input_str)
    except json.JSONDecodeError:
        return {"error": f"Invalid JSON input to BatchReviewControls: {tool_input_str}"}

    controls = tool_input.get('controls')
    review_types = tool_input.get('review_types')

    if not isinstance(controls, list) or not isinstance(review_types, list):
        return {"error": "Invalid input format. 'controls' and 'review_types' must be lists."}
    
    if not controls:
        return {"error": "'controls' list cannot be empty."}
    if not review_types:
        return {"error": "'review_types' list cannot be empty."}

    if len(controls) > 10:
        # Returning a dict that can be JSON serialized, instead of raising ValueError directly
        # The agent should be able to handle this error response.
        return {"error": "Can only review up to 10 controls at a time."}
    
    results = {}
    for c in controls:
        if not isinstance(c, dict):
            results[str(c)] = {"error": "Each item in 'controls' must be a dictionary."}
            continue
        cid = c.get("control_id", "<no-id>")
        results[cid] = {r: single_review(c, r) for r in review_types}
    return results

review_tool = Tool(
    name="BatchReviewControls",
    func=batch_review_func, # Renamed internal function to avoid conflict with tool name
    description=(
        "Run 5W, OE, DE reviews on up to 10 controls. "
        "Args: Expects a single JSON string or dictionary with two keys: 'controls' (list of control objects) and 'review_types' (list of strings, e.g. ['5W','OE','DE'])."
    )
)

# Explain methods tool
def explain_methods_func(_: str = None) -> str: # Added default for input
    return chain_methods.run({}) # Pass empty dict if no input var in prompt

methods_tool = Tool(
    name="ExplainMethods",
    func=explain_methods_func, # Renamed internal function
    description="Explain how 5W, OE, and DE analyses are performed."
)

# Tool: Update Prompt
@tool
def update_prompt_tool(prompt_key: str, new_template_string: str) -> str:
    """
    Updates the template for a specified analysis type (e.g., '5W', 'OE', 'DE').
    Args:
        prompt_key (str): The key of the prompt to update (e.g., '5W', 'OE', 'DE', 'METHODS').
        new_template_string (str): The new template string. Must include required input variables like '{control}'.
    """
    success = prompts.update_prompt(prompt_key, new_template_string)
    if success:
        updated_prompt_template = prompts.get_prompt(prompt_key)
        if updated_prompt_template and prompt_key in ANALYSIS_CHAINS:
            ANALYSIS_CHAINS[prompt_key].prompt = updated_prompt_template
            # Also update the global prompt variables in prompts.py if they are directly used (handled in prompts.update_prompt)
            return f"Prompt '{prompt_key}' updated successfully."
        elif not updated_prompt_template:
            return f"Error: Prompt '{prompt_key}' template object not found after update."
        else: # prompt_key not in ANALYSIS_CHAINS (e.g. if it was some other prompt)
            return f"Prompt template for '{prompt_key}' updated in prompts module, but no corresponding chain found in tools.py to update."
    return f"Failed to update prompt '{prompt_key}'. Key not found or error during update."

# Export all tools
TOOLS = [filter_tool, review_tool, methods_tool, update_prompt_tool] 