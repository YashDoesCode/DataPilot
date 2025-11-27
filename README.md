# DataPilot

**Intelligent Experiment Assistant for Kaggle**

## Overview

DataPilot is an autonomous AI agent designed to accelerate data science workflows. It plans experiments, executes code, and logs results automatically.

## Setup

1.  `pip install -r requirements.txt`
2.  `export GEMINI_API_KEY="your_key"`

## Usage

**Notebook:**

```python
from agent_main import run_agent_session
run_agent_session(goal="Build a baseline model", data_path="/kaggle/input/data")
```

**CLI:**

```bash
python agent_main.py --goal "Analyze dataset" --offline
```

## Features

- **Auto-Coding**: Generates and runs Python code.
- **Data Insight**: Summarizes datasets automatically.
- **Experiment Logging**: Tracks all runs in JSON.
- **Offline Mode**: Works without API access (mock mode).
