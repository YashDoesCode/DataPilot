# DataPilot

**Autopilot for Data Science**

## Problem Statement

Data science competitions and real-world projects involve repetitive tasks: exploring data, setting up baselines, tuning hyperparameters, and logging results. Managing these experiments while keeping track of code versions and insights can be overwhelming. **DataPilot** solves this by acting as an intelligent pair programmer that can plan, execute, and log experiments autonomously.

## Architecture

The project is designed as a modular agent framework:

- **`config.py`**: Centralized configuration for API keys, model parameters, and paths.
- **`system_instructions.md`**: The "brain" of the agent, defining its persona and capabilities.
- **`tools.py`**: A suite of safe, sandboxed functions for data loading, code execution, and logging.
- **`agent_core.py`**: The main logic that orchestrates the ReAct (Reasoning + Acting) loop.
- **`agent_main.py`**: Entry point for CLI and Notebook usage.

## Setup

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure API Key**:
    Set your Gemini API key as an environment variable:
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```
    _In Kaggle, use the "Secrets" add-on to securely store `GEMINI_API_KEY`._

## Usage

### In a Kaggle Notebook

Import the runner function and start a session:

```python
from agent_main import run_agent_session

# Define your goal
goal = "Load the Titanic dataset, clean missing values, and train a Random Forest classifier."

# Run the agent
run_agent_session(goal=goal, data_path="/kaggle/input/titanic")
```

### From Command Line

```bash
python agent_main.py --goal "Analyze the housing dataset" --offline
```

_(Use `--offline` to test without an API key using mock responses)_

## Agentic Behavior

DataPilot follows a **ReAct** pattern:

1.  **Thought**: It analyzes the user request and plans the next step.
2.  **Action**: It calls a specific tool (e.g., `load_data` or `execute_code`).
3.  **Observation**: It reads the tool's output (e.g., dataframe columns or model accuracy).
4.  **Iteration**: It repeats this cycle until the goal is met.

## Safety & Limitations

- **Sandboxed Execution**: Code is executed in a restricted environment, but users should still review generated code.
- **No Internet Access (Default)**: The agent relies on local libraries and data.
- **Hallucinations**: Like all LLMs, it may occasionally generate incorrect code or facts. Always verify important results.

## Kaggle Competition Alignment

This project demonstrates:

- **Real-world relevance**: Directly aids the core activity of Kaggle users.
- **Modular Design**: Clean separation of concerns.
- **Reproducibility**: Structured logging ensures experiments are trackable.
