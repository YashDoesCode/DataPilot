import os
import json
from typing import List, Dict, Any
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None

from config import default_config
from tools import AVAILABLE_TOOLS

class KaggleExperimentAssistantAgent:
    def __init__(self):
        self.config = default_config
        self.system_instructions = self._load_instructions()
        self.model = self._init_model()

    def _load_instructions(self) -> str:
        try:
            with open(os.path.join(os.path.dirname(__file__), "system_instructions.md"), 'r') as f:
                return f.read()
        except:
            return "You are a helpful Kaggle assistant."

    def _init_model(self):
        if self.config.kaggle.offline_mode or not self.config.gemini.api_key or not genai:
            self.config.kaggle.offline_mode = True
            return None
        genai.configure(api_key=self.config.gemini.api_key)
        return genai.GenerativeModel(
            model_name=self.config.gemini.model_name,
            generation_config=genai.GenerationConfig(
                temperature=self.config.gemini.temperature,
                top_p=self.config.gemini.top_p,
                top_k=self.config.gemini.top_k,
                max_output_tokens=self.config.gemini.max_output_tokens,
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
            system_instruction=self.system_instructions
        )

    def _call_gemini(self, prompt: str) -> str:
        if self.config.kaggle.offline_mode:
            if "list_files" in prompt: return 'Thought: Check files.\nAction: list_files("/kaggle/input")'
            if "load_data" in prompt: return 'Thought: Load data.\nAction: load_data("/kaggle/input/train.csv")'
            return 'Final Answer: Mock response.'
        try:
            if not hasattr(self, 'chat'): self.chat = self.model.start_chat(history=[])
            return self.chat.send_message(prompt).text
        except Exception as e:
            return f"Error: {e}"

    def _parse(self, response: str):
        for line in response.split('\n'):
            if line.startswith("Action:"):
                content = line[len("Action:"):].strip()
                if "(" in content and content.endswith(")"):
                    return "TOOL", (content.split("(")[0], content[content.find("(")+1:-1])
            if line.startswith("Final Answer:"):
                return "FINAL", line[len("Final Answer:"):].strip()
        return "TEXT", response

    def _exec_tool(self, name: str, args: str) -> str:
        if name not in AVAILABLE_TOOLS: return f"Error: Tool '{name}' not found."
        try:
            return str(AVAILABLE_TOOLS[name](*eval(f"[{args}]", {"__builtins__": {}})))
        except Exception as e:
            return f"Error: {e}"

    def run_workflow(self, goal: str):
        print(f"--- Starting Session ---\nGoal: {goal}")
        if self.model: self.chat = self.model.start_chat(history=[])
        curr = f"Goal: {goal}\nStart."
        for i in range(self.config.agent.max_steps):
            print(f"\n[Step {i+1}]")
            resp = self._call_gemini(curr)
            print(f"Agent: {resp}")
            type_, content = self._parse(resp)
            if type_ == "FINAL":
                print(f"Done: {content}")
                break
            elif type_ == "TOOL":
                name, args = content
                print(f"Call: {name}({args})")
                res = self._exec_tool(name, args)
                print(f"Out: {res[:200]}...")
                curr = f"Observation: {res}"
            else:
                curr = "Continue."
