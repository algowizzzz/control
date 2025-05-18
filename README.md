# Control Review Agent: A LangChain-based conversational assistant for PRC library control analysis.

## Features

- Conversational filtering by control ID or attributes
- 5W, Operational Effectiveness (OE), Design Effectiveness (DE) reviews (max 10 controls at once)
- Self-awareness: introspection of tools, data, and prompts
- Dynamic prompt customization at runtime
- Smooth, fluid user-agent interaction via Claude

## Structure

```
control-review-agent/
├── controls.json               # PRC Library (18k controls)
├── README.md                   # Project overview
├── requirements.txt            # Python dependencies
└── src/
    ├── data_loader.py         # JSON loading & filtering
    ├── prompts.py             # PromptTemplate definitions
    ├── tools.py               # Tool wrappers for LangChain
    ├── agent.py               # Agent initialization & persona
    └── examples/
        └── sample_run.py      # Demonstration scenarios

```



## Running Examples

1.  **Set up the Environment:**
    *   Ensure you have Python 3 installed.
    *   Create and activate a virtual environment:
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Create a `.env` file in the project root (`control-1/`) and add your Anthropic API key:
        ```
        ANTHROPIC_API_KEY='your_anthropic_api_key_here'
        ```

2.  **Run the Demonstration Script:**
    *   To see a predefined set of demonstration scenarios, run `sample_run.py` as a module from the project root directory (`control-1/`):
        ```bash
        python -m src.examples.sample_run
        ```

3.  **Run the Interactive Chat:**
    *   To chat with the agent interactively, run `interactive_chat.py` as a module from the project root directory (`control-1/`):
        ```bash
        python -m src.examples.interactive_chat
        ``` 