"""
Configuration module for the Kaggle Experiment Assistant Agent (KEAA).

This module defines configuration classes for the Gemini API, agent behavior,
and Kaggle environment settings. It handles loading API keys from environment
variables and provides default settings for the agent.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GeminiConfig:
    """
    Configuration for the Gemini API.
    """
    model_name: str = "gemini-2.5-pro"
    api_key: Optional[str] = field(default_factory=lambda: os.environ.get("GEMINI_API_KEY"))
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 64
    max_output_tokens: int = 8192

    def validate(self) -> bool:
        """Checks if the API key is set."""
        if not self.api_key:
            # In a real scenario, we might want to raise an error or warn.
            # For now, we'll just return False, allowing offline mode to proceed.
            return False
        return True

@dataclass
class AgentConfig:
    """
    Configuration for the Agent's behavior.
    """
    max_steps: int = 10  # Maximum number of reasoning steps per user request
    max_experiments: int = 5 # Limit on number of distinct experiments to run in a session
    verbose: bool = True # Whether to print detailed logs to stdout
    safety_mode: bool = True # Enable strict safety checks (e.g. no shell commands)

@dataclass
class KaggleConfig:
    """
    Configuration for the Kaggle environment.
    """
    input_dir: str = "/kaggle/input"
    working_dir: str = "/kaggle/working"
    experiments_dir: str = "/kaggle/working/experiments"
    offline_mode: bool = False # Set to True to disable actual API calls (mock mode)

    def __post_init__(self):
        # Ensure experiment directory exists if we are in a writable environment
        # We use a try-except block because in some read-only envs this might fail,
        # though /kaggle/working is usually writable.
        try:
            os.makedirs(self.experiments_dir, exist_ok=True)
        except OSError:
            pass

class Config:
    """
    Main configuration container.
    """
    def __init__(self):
        self.gemini = GeminiConfig()
        self.agent = AgentConfig()
        self.kaggle = KaggleConfig()

    def __repr__(self):
        return (f"Config(gemini={self.gemini}, agent={self.agent}, kaggle={self.kaggle})")

# Global configuration instance
default_config = Config()
