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
        if not self.api_key:
            return False
        return True

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
        if not os.path.exists("/kaggle/working"):
            base_dir = os.getcwd()
            self.working_dir = os.path.join(base_dir, "output")
            self.experiments_dir = os.path.join(self.working_dir, "experiments")
            if not os.path.exists("/kaggle/input"):
                self.input_dir = os.path.join(base_dir, "data")
            
            print(f"Notice: Running locally. Output directory set to: {self.working_dir}")

        try:
            os.makedirs(self.experiments_dir, exist_ok=True)
        except OSError:
            pass

class Config:
    def __init__(self):
        self.gemini = GeminiConfig()
        self.agent = AgentConfig()
        self.kaggle = KaggleConfig()

    def __repr__(self):
        return (f"Config(gemini={self.gemini}, agent={self.agent}, kaggle={self.kaggle})")

default_config = Config()
