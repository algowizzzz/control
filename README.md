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

```bash
python src/examples/sample_run.py

``` 