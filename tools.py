import os
import json
import pandas as pd
import numpy as np
import datetime
from typing import Dict, List, Any, Optional, Union
import traceback
import io
import sys

try:
    from config import default_config
except ImportError:
    from dataclasses import dataclass
    @dataclass
    class MockConfig:
        kaggle = type('obj', (object,), {'experiments_dir': '/kaggle/working/experiments'})
    default_config = type('obj', (object,), {'kaggle': MockConfig()})

def list_files(directory: str) -> List[str]:
    file_list = []
    if not os.path.exists(directory):
        return [f"Error: Directory '{directory}' does not exist."]
    
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
            if nrows:
                df = df.head(nrows)
        else:
            return f"Error: Unsupported file format for '{filepath}'. Use CSV or Parquet."

        buffer = io.StringIO()
        df.info(buf=buffer)
        info_str = buffer.getvalue()
        
        return f"Successfully loaded '{filepath}'.\nShape: {df.shape}\n\nInfo:\n{info_str}\n\nFirst 5 rows:\n{df.head().to_string()}"
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
            
        desc = df.describe(include='all').to_string()
        missing = df.isnull().sum().to_string()
        
        return f"Descriptive Statistics:\n{desc}\n\nMissing Values:\n{missing}"
    except Exception as e:
        return f"Error summarizing data: {str(e)}"

def execute_code(code: str) -> str:
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    
    local_scope = {}
    global_scope = {
        "pd": pd,
        "np": np,
        "os": os,
        "json": json,
    }
    
    try:
        exec(code, global_scope, local_scope)
        output = redirected_output.getvalue()
        return f"Execution Success:\n{output}"
    except Exception:
        error_msg = traceback.format_exc()
        return f"Execution Error:\n{error_msg}"
    finally:
        sys.stdout = old_stdout

def log_experiment(experiment_data: Dict[str, Any]) -> str:
    try:
        if "timestamp" not in experiment_data:
            experiment_data["timestamp"] = datetime.datetime.now().isoformat()
            
        log_dir = default_config.kaggle.experiments_dir
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "experiment_log.json")
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                    if not isinstance(logs, list):
                        logs = []
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []
            
        logs.append(experiment_data)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
        return f"Experiment logged successfully to {log_file}."
    except Exception as e:
        return f"Error logging experiment: {str(e)}"

def save_text(filename: str, content: str) -> str:
    try:
        filepath = os.path.join(default_config.kaggle.working_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"File saved to {filepath}."
    except Exception as e:
        return f"Error saving file: {str(e)}"

AVAILABLE_TOOLS = {
    "list_files": list_files,
    "load_data": load_data,
    "summarize_data": summarize_data,
    "execute_code": execute_code,
    "log_experiment": log_experiment,
    "save_text": save_text
}
