import os
import json
import pandas as pd
import numpy as np
import datetime
import traceback
import io
import sys
from typing import List, Dict, Any, Optional

try:
    from config import default_config
except ImportError:
    from dataclasses import dataclass
    @dataclass
    class MockConfig:
        kaggle = type('obj', (object,), {'experiments_dir': '/kaggle/working/experiments'})
    default_config = type('obj', (object,), {'kaggle': MockConfig()})

def list_files(directory: str) -> List[str]:
    if not os.path.exists(directory):
        return [f"Error: Directory '{directory}' does not exist."]
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def load_data(filepath: str, nrows: Optional[int] = None) -> str:
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath, nrows=nrows)
        elif filepath.endswith('.parquet'):
            df = pd.read_parquet(filepath)
            if nrows: df = df.head(nrows)
        else:
            return f"Error: Unsupported file format for '{filepath}'."
        buffer = io.StringIO()
        df.info(buf=buffer)
        return f"Loaded '{filepath}'.\nShape: {df.shape}\nInfo:\n{buffer.getvalue()}\nHead:\n{df.head().to_string()}"
    except Exception as e:
        return f"Error loading data: {str(e)}"

def summarize_data(filepath: str) -> str:
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith('.parquet'):
            df = pd.read_parquet(filepath)
        else:
            return "Error: Unsupported file format."
        return f"Stats:\n{df.describe(include='all').to_string()}\nMissing:\n{df.isnull().sum().to_string()}"
    except Exception as e:
        return f"Error summarizing data: {str(e)}"

def execute_code(code: str) -> str:
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        exec(code, {"pd": pd, "np": np, "os": os, "json": json}, {})
        return f"Success:\n{sys.stdout.getvalue()}"
    except Exception:
        return f"Error:\n{traceback.format_exc()}"
    finally:
        sys.stdout = old_stdout

def log_experiment(data: Dict[str, Any]) -> str:
    try:
        if "timestamp" not in data: data["timestamp"] = datetime.datetime.now().isoformat()
        log_dir = default_config.kaggle.experiments_dir
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "experiment_log.json")
        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try: logs = json.load(f)
                except: pass
        logs.append(data)
        with open(log_file, 'w') as f: json.dump(logs, f, indent=2)
        return f"Logged to {log_file}."
    except Exception as e:
        return f"Error logging: {str(e)}"

def save_text(filename: str, content: str) -> str:
    try:
        path = os.path.join(default_config.kaggle.working_dir, filename)
        with open(path, 'w') as f: f.write(content)
        return f"Saved to {path}."
    except Exception as e:
        return f"Error saving: {str(e)}"

AVAILABLE_TOOLS = {
    "list_files": list_files,
    "load_data": load_data,
    "summarize_data": summarize_data,
    "execute_code": execute_code,
    "log_experiment": log_experiment,
    "save_text": save_text
}
