import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class GeminiConfig:
    model_name: str = "gemini-2.5-pro"
    api_key: Optional[str] = field(default_factory=lambda: os.environ.get("GEMINI_API_KEY"))
    temperature: float = 0.7
    top_p: float = 0.95
    top_k: int = 64
    max_output_tokens: int = 8192

    def validate(self) -> bool:
        return bool(self.api_key)

@dataclass
class AgentConfig:
    max_steps: int = 10
    max_experiments: int = 5
    verbose: bool = True
    safety_mode: bool = True

@dataclass
class KaggleConfig:
    input_dir: str = "/kaggle/input"
    working_dir: str = "/kaggle/working"
    experiments_dir: str = "/kaggle/working/experiments"
    offline_mode: bool = False

    def __post_init__(self):
        try:
            os.makedirs(self.experiments_dir, exist_ok=True)
        except OSError:
            pass

class Config:
    def __init__(self):
        self.gemini = GeminiConfig()
        self.agent = AgentConfig()
        self.kaggle = KaggleConfig()

default_config = Config()
