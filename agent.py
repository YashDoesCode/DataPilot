import os
import json
import pandas as pd
from typing import List, Dict, Any
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None

class DataPilot:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = self._init_model()
        self.tools = {
            "list_files": self.list_files,
            "load_data": self.load_data,
            "summarize_data": self.summarize_data,
            "execute_code": self.execute_code
        }

    def _init_model(self):
        if not self.api_key or not genai: return None
        genai.configure(api_key=self.api_key)
        return genai.GenerativeModel(
            model_name="gemini-2.5-pro",
            generation_config={"response_mime_type": "application/json"},
            safety_settings={HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE},
            system_instruction="You are DataPilot. Respond in JSON: {thought: string, tool_name: string, tool_args: list} or {thought: string, final_answer: string}. No m-dashes."
        )

    def list_files(self, directory="."):
        try: return str(os.listdir(directory))
        except Exception as e: return str(e)

    def load_data(self, filepath, nrows=5):
        try: return str(pd.read_csv(filepath, nrows=nrows).to_dict())
        except Exception as e: return str(e)

    def summarize_data(self, filepath):
        try: return str(pd.read_csv(filepath).describe().to_dict())
        except Exception as e: return str(e)

    def execute_code(self, code):
        try:
            local_vars = {}
            exec(code, {}, local_vars)
            return str(local_vars)
        except Exception as e: return str(e)

    def chat(self, prompt):
        if not self.model: return json.dumps({"final_answer": "Offline mode."})
        try:
            resp = self.model.generate_content(prompt)
            return resp.text
        except Exception as e: return json.dumps({"final_answer": f"Error: {e}"})

    def execute_tool(self, tool_name, args):
        if tool_name not in self.tools: return "Tool not found"
        try: return self.tools[tool_name](*args)
        except Exception as e: return str(e)
