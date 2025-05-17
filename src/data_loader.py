import json
import pandas as pd
from typing import List, Dict, Any, Optional

# Load control library once
_controls = []
_df_controls = pd.DataFrame() # Initialize an empty DataFrame

try:
    # Adjusted path to be relative to the project root when script is run from there
    with open("controls.json", "r") as f:
        _controls = json.load(f)
    _df_controls = pd.DataFrame(_controls)
    if _df_controls.empty and _controls: # Handles case where _controls is not empty but results in empty DF (e.g. list of non-dicts)
        print("Warning: controls.json was loaded but resulted in an empty DataFrame. Ensure it's a list of dictionaries.")
    elif not _controls and not _df_controls.empty: # Should not happen if logic is sound, but as a safeguard
        print("Warning: DataFrame is not empty but original control list is. Check data loading logic.")
    elif not _controls:
        print("Warning: controls.json is empty or not a valid list of controls. DataFrame is empty.")

except FileNotFoundError:
    print("Error: controls.json not found in the project root directory. DataFrame will be empty.")
except json.JSONDecodeError:
    print("Error: Could not decode controls.json. Ensure it is valid JSON. DataFrame will be empty.")
except Exception as e:
    print(f"An unexpected error occurred during data loading: {e}. DataFrame will be empty.")


def filter_controls(control_ids: Optional[List[str]] = None, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Return list of controls matching all filters (substring, case-insensitive).
    Skips filters for attributes not present in the DataFrame.
    """
    global _df_controls
    if _df_controls.empty:
        print("Warning: Filtering attempted on an empty controls DataFrame.")
        return []

    # The new wrapper in tools.py (filter_controls_tool_func) now handles various input string formats
    # and ensures that 'control_ids' is a list (if provided) and 'filters' is a dict (if provided).
    # So, the isinstance(filters, str) check is no longer needed here.

    filtered_df = _df_controls.copy()

    if control_ids: # control_ids is now expected to be a list of strings or None
        # Ensure control_ids is a list, even if it was a single string passed to the wrapper
        # (The wrapper should already ensure this, but as a safeguard for direct calls)
        if not isinstance(control_ids, list):
            # This case should ideally not be hit if called via the tool wrapper
            print(f"Warning: filter_controls received non-list for control_ids: {control_ids}. Wrapping in list.")
            control_ids = [str(control_ids)] # Convert to string just in case, then listify
        
        # Filter by control_id - convert DataFrame's control_id column to string for robust comparison
        # if it's not already, to avoid issues with mixed types (e.g. int IDs in JSON vs str here)
        if 'control_id' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['control_id'].astype(str).isin([str(cid) for cid in control_ids])]
        else:
            print("Warning: 'control_id' column not found in DataFrame. Cannot filter by control_ids.")
            return [] # Or return all if no control_id column?

    elif filters: # filters is now expected to be a dictionary or None
        if not isinstance(filters, dict):
            # This case should ideally not be hit if called via the tool wrapper
            print(f"Error: filter_controls received non-dict for filters: {filters}. Cannot apply filters.")
            return [] # Or based on requirements, return filtered_df if only control_ids was meant to be used
        
        for attr, val in filters.items():
            if attr in filtered_df.columns:
                # Ensure the column is treated as string for contains, handle NaNs
                filtered_df = filtered_df[filtered_df[attr].astype(str).str.contains(val, case=False, na=False)]
            else:
                print(f"Warning: Filter attribute '{attr}' not found in controls. Skipping this filter.")

    return filtered_df.to_dict(orient="records") 