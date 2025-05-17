from langchain.prompts import PromptTemplate

# Initial prompt templates

INITIAL_PROMPTS = {
    "5W": """
You are a control-review expert. Perform a comprehensive 5W analysis (Who, What, Where, When, and Why) for the given control. Your response must be detailed, insightful, and at least 200 words. Be sure to:
- Clearly address each of the 5Ws in separate sections.
- Provide context, scope, and impact of the control.
- Explain the significance of each aspect and how it relates to the control's effectiveness.
- Use examples or hypothetical scenarios if helpful.
- Write in a professional, analytical, and thorough manner.

{control}
""",
    "OE": """
You are an AI specialized in control assessments. Provide a detailed review (minimum 200 words) evaluating the operational effectiveness of this control. Your analysis should:
- Discuss how the control is executed in practice, including roles and responsibilities.
- Describe monitoring mechanisms and how performance is tracked.
- Identify relevant performance metrics and how they are measured.
- Highlight strengths, weaknesses, and any observed issues in operationalization.
- Offer recommendations for improvement if applicable.
- Write in a clear, structured, and analytical style.

{control}
""",
    "DE": """
You are an AI specialized in control assessments. Write a comprehensive review (at least 200 words) evaluating the design effectiveness of this control. Your review should:
- Analyze the structure and clarity of the control's documentation.
- Assess alignment with objectives, policies, and regulatory requirements.
- Evaluate risk coverage and whether the design addresses key threats.
- Discuss any gaps, redundancies, or areas for enhancement in the design.
- Provide actionable suggestions for improving design effectiveness.
- Ensure your response is thorough, well-organized, and professional.

{control}
""",
    "METHODS": """
Explain your review methodologies:

- 5W analysis
- Operational effectiveness assessment
- Design effectiveness assessment
"""
}

# Store PromptTemplate objects in a dictionary
PROMPT_TEMPLATES = {
    key: PromptTemplate.from_template(template)
    for key, template in INITIAL_PROMPTS.items()
}

# Export individual prompt objects for direct use if needed by current tool structure,
# but encourage using PROMPT_TEMPLATES["key"]
prompt_5w = PROMPT_TEMPLATES["5W"]
prompt_oe = PROMPT_TEMPLATES["OE"]
prompt_de = PROMPT_TEMPLATES["DE"]
prompt_methods = PROMPT_TEMPLATES["METHODS"]

def get_prompt(prompt_key: str) -> PromptTemplate:
    """Returns the current PromptTemplate object for a given key."""
    return PROMPT_TEMPLATES.get(prompt_key)

def update_prompt(prompt_key: str, new_template_string: str) -> bool:
    """Updates the prompt template for a given key and returns True if successful."""
    if prompt_key in PROMPT_TEMPLATES:
        try:
            PROMPT_TEMPLATES[prompt_key] = PromptTemplate.from_template(new_template_string)
            # Update the exported global variables as well if they are still being used directly elsewhere
            # This is a bit of a workaround for direct global var usage.
            # Ideally, all usages would go via get_prompt or directly use the chains which will be updated.
            if prompt_key == "5W":
                global prompt_5w
                prompt_5w = PROMPT_TEMPLATES[prompt_key]
            elif prompt_key == "OE":
                global prompt_oe
                prompt_oe = PROMPT_TEMPLATES[prompt_key]
            elif prompt_key == "DE":
                global prompt_de
                prompt_de = PROMPT_TEMPLATES[prompt_key]
            elif prompt_key == "METHODS":
                global prompt_methods
                prompt_methods = PROMPT_TEMPLATES[prompt_key]
            return True
        except Exception as e:
            print(f"Error updating prompt {prompt_key}: {e}")
            return False
    return False 