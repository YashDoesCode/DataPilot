import os
import json
import time
from typing import List, Dict, Any, Optional
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    genai = None
    HarmCategory = None
    HarmBlockThreshold = None

from config import default_config
from tools import AVAILABLE_TOOLS

class KaggleExperimentAssistantAgent:

    def __init__(self):
        self.config = default_config
        self.history: List[Dict[str, Any]] = []
        self.system_instructions = self._load_system_instructions()
        self.model = self._initialize_model()
        
        self.experiments_run = 0

    def _load_system_instructions(self) -> str:
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "system_instructions.md")
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            return "You are a helpful Kaggle assistant."

    def _initialize_model(self):
        if self.config.kaggle.offline_mode:
            return None

        if not self.config.gemini.api_key:
            self.config.kaggle.offline_mode = True
            return None

        if genai is None:
            self.config.kaggle.offline_mode = True
            return None

        genai.configure(api_key=self.config.gemini.api_key)
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        model = genai.GenerativeModel(
            model_name=self.config.gemini.model_name,
            generation_config=genai.GenerationConfig(
                temperature=self.config.gemini.temperature,
                top_p=self.config.gemini.top_p,
                top_k=self.config.gemini.top_k,
                max_output_tokens=self.config.gemini.max_output_tokens,
                response_mime_type="application/json"
            ),
            safety_settings=safety_settings,
            system_instruction=self.system_instructions
        )
        return model

    def _call_gemini(self, prompt: str) -> str:
        if self.config.kaggle.offline_mode:
            return self._mock_response(prompt)

        try:
            if not hasattr(self, 'chat_session') or self.chat_session is None:
                self.chat_session = self.model.start_chat(history=[])
            
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            return json.dumps({"thought": "Error calling API", "final_answer": str(e)})

    def _mock_response(self, prompt: str) -> str:
        if "list_files" in prompt:
            return json.dumps({
                "thought": "I should check the files.",
                "tool_name": "list_files",
                "tool_args": ["/kaggle/input"]
            })
        elif "load_data" in prompt:
            return json.dumps({
                "thought": "I will load the data.",
                "tool_name": "load_data",
                "tool_args": ["/kaggle/input/train.csv"]
            })
        else:
            return json.dumps({
                "thought": "I am in offline mode.",
                "final_answer": "This is a mock response in offline mode."
            })

    def _parse_response(self, response: str):
        try:
            data = json.loads(response)
            
            if "tool_name" in data and data["tool_name"]:
                tool_name = data["tool_name"]
                tool_args = data.get("tool_args", [])
                
                if isinstance(tool_args, list):
                    args_str = ", ".join([repr(arg) for arg in tool_args])
                else:
                    args_str = str(tool_args)
                    
                return "TOOL", (tool_name, args_str)
            
            elif "final_answer" in data:
                return "FINAL", data["final_answer"]
            
            else:
                return "TEXT", str(data)
                
        except json.JSONDecodeError:
            return "TEXT", response

    def _execute_tool(self, tool_name: str, args_str: str) -> str:
        if tool_name not in AVAILABLE_TOOLS:
            return f"Error: Tool '{tool_name}' not found."
        
        func = AVAILABLE_TOOLS[tool_name]
        
        try:
            args = eval(f"[{args_str}]", {"__builtins__": {}})
            result = func(*args)
            return str(result)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"

    def run_workflow(self, user_goal: str):
        print(f"--- Starting Agent Session ---\nGoal: {user_goal}\n")
        
        if self.model:
            self.chat_session = self.model.start_chat(history=[])
        
        step_count = 0
        current_input = f"User Goal: {user_goal}"
        
        while step_count < self.config.agent.max_steps:
            step_count += 1
            print(f"\n[Step {step_count}]")
            
            response_text = self._call_gemini(current_input)
            print(f"Agent: {response_text}")
            
            msg_type, content = self._parse_response(response_text)
            
            if msg_type == "FINAL":
                print(f"\n--- Task Completed ---\nFinal Answer: {content}")
                break
            
            elif msg_type == "TOOL":
                tool_name, args_str = content
                print(f"Tool Call: {tool_name}({args_str})")
                
                tool_result = self._execute_tool(tool_name, args_str)
                
                display_result = tool_result[:500] + "..." if len(tool_result) > 500 else tool_result
                print(f"Tool Output: {display_result}")
                
                current_input = f"Observation: {tool_result}"
                
            else:
                current_input = "Please continue."
                
        if step_count >= self.config.agent.max_steps:
            print("\n--- Max Steps Reached ---")

if __name__ == "__main__":
    agent = KaggleExperimentAssistantAgent()
