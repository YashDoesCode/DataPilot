"""
Agent Core module for the Kaggle Experiment Assistant Agent (KEAA).

This module defines the `KaggleExperimentAssistantAgent` class, which orchestrates
the interaction between the user, the Gemini model, and the Kaggle environment tools.
"""

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
    """
    The main agent class responsible for managing the experiment session.
    """

    def __init__(self):
        """
        Initializes the agent with configuration and system instructions.
        """
        self.config = default_config
        self.history: List[Dict[str, Any]] = []
        self.system_instructions = self._load_system_instructions()
        self.model = self._initialize_model()
        
        # Internal memory for the current session
        self.experiments_run = 0

    def _load_system_instructions(self) -> str:
        """Loads the system prompt from the markdown file."""
        try:
            # Assuming the file is in the same directory or a known location
            # For Kaggle, we might need to adjust this path if files are moved
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, "system_instructions.md")
            with open(path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            print("Warning: system_instructions.md not found. Using default minimal prompt.")
            return "You are a helpful Kaggle assistant."

    def _initialize_model(self):
        """Initializes the Gemini model client."""
        if self.config.kaggle.offline_mode:
            print("Agent initialized in OFFLINE mode. No API calls will be made.")
            return None

        if not self.config.gemini.api_key:
            print("Warning: GEMINI_API_KEY not found. Switching to OFFLINE mode.")
            self.config.kaggle.offline_mode = True
            return None

        if genai is None:
            print("Warning: google-generativeai package not found. Switching to OFFLINE mode.")
            self.config.kaggle.offline_mode = True
            return None

        genai.configure(api_key=self.config.gemini.api_key)
        
        # Safety settings - we can be relatively permissive as we are in a coding environment
        # but still want to block harmful content.
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
            ),
            safety_settings=safety_settings,
            system_instruction=self.system_instructions
        )
        return model

    def _call_gemini(self, prompt: str) -> str:
        """
        Sends a prompt to Gemini and returns the text response.
        Handles offline mode by returning a mock response.
        """
        if self.config.kaggle.offline_mode:
            return self._mock_response(prompt)

        try:
            # We use the chat session if we want to maintain history automatically,
            # but here we are managing history manually for more control over the prompt structure
            # or we could use start_chat. Let's use generate_content for single turns 
            # with history included in the prompt if needed, or better, use a chat session.
            
            # For this implementation, let's assume we pass the full history or use a chat object.
            # To keep it simple and stateless between method calls, let's use a chat session 
            # that persists as an attribute if we were doing a continuous chat.
            # However, for the 'run_step' logic, we might want to just send the current state.
            
            # Let's use a fresh chat session for the 'run_workflow' but here we just generate content.
            # Ideally, we should maintain a chat object. Let's refactor __init__ to create one?
            # Actually, let's just use generate_content with the accumulated history formatted as text
            # OR use the chat object. The chat object is easier.
            
            if not hasattr(self, 'chat_session') or self.chat_session is None:
                self.chat_session = self.model.start_chat(history=[])
            
            response = self.chat_session.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"Error calling Gemini: {e}")
            return f"Error: {str(e)}"

    def _mock_response(self, prompt: str) -> str:
        """Generates a mock response for offline testing."""
        if "list_files" in prompt:
            return 'Thought: I should check the files.\nAction: list_files("/kaggle/input")'
        elif "load_data" in prompt:
            return 'Thought: I will load the data.\nAction: load_data("/kaggle/input/train.csv")'
        else:
            return 'Final Answer: This is a mock response in offline mode.'

    def _parse_response(self, response: str):
        """
        Parses the model's response to identify tool calls.
        Expected format:
        Thought: ...
        Action: tool_name(arguments)
        ...
        """
        lines = response.split('\n')
        tool_call = None
        thought = ""
        
        for line in lines:
            if line.startswith("Action:"):
                # Extract tool name and args
                # Format: Action: tool_name("arg1", arg2)
                content = line[len("Action:"):].strip()
                if "(" in content and content.endswith(")"):
                    tool_name = content.split("(")[0]
                    args_str = content[len(tool_name)+1:-1]
                    tool_call = (tool_name, args_str)
            elif line.startswith("Thought:"):
                thought += line[len("Thought:"):].strip() + " "
            elif line.startswith("Final Answer:"):
                return "FINAL", line[len("Final Answer:"):].strip()
        
        if tool_call:
            return "TOOL", tool_call
        
        # If no explicit action or final answer, treat as text
        return "TEXT", response

    def _execute_tool(self, tool_name: str, args_str: str) -> str:
        """Executes a tool by name with the given arguments string."""
        if tool_name not in AVAILABLE_TOOLS:
            return f"Error: Tool '{tool_name}' not found."
        
        func = AVAILABLE_TOOLS[tool_name]
        
        # Naive argument parsing (in a real app, use a robust parser or JSON)
        # We'll try to eval the args_str as a python tuple/args
        # This is risky if the model outputs complex python objects, but for strings it's okay-ish
        # Better: instruct model to output JSON args.
        # For this simplified version, let's try to parse manually or use eval safely.
        try:
            # We wrap args in a list to handle single vs multiple args
            # This is a bit hacky. A better way is to ask the model for JSON.
            # Let's assume the model outputs valid python literal args.
            # e.g. "/path/to/file" or "/path", 5
            
            # Safety check: only allow literals
            # In a real Kaggle comp, we might want stricter parsing.
            args = eval(f"[{args_str}]", {"__builtins__": {}})
            
            result = func(*args)
            return str(result)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {e}"

    def run_workflow(self, user_goal: str):
        """
        Runs the main agent loop to achieve the user's goal.
        """
        print(f"--- Starting Agent Session ---\nGoal: {user_goal}\n")
        
        # Reset session
        if self.model:
            self.chat_session = self.model.start_chat(history=[])
        
        step_count = 0
        current_input = f"User Goal: {user_goal}\nPlease start by listing files or planning your approach."
        
        while step_count < self.config.agent.max_steps:
            step_count += 1
            print(f"\n[Step {step_count}]")
            
            # 1. Get response from Gemini
            response_text = self._call_gemini(current_input)
            print(f"Agent: {response_text}")
            
            # 2. Parse response
            msg_type, content = self._parse_response(response_text)
            
            if msg_type == "FINAL":
                print(f"\n--- Task Completed ---\nFinal Answer: {content}")
                break
            
            elif msg_type == "TOOL":
                tool_name, args_str = content
                print(f"Tool Call: {tool_name}({args_str})")
                
                # 3. Execute Tool
                tool_result = self._execute_tool(tool_name, args_str)
                
                # Truncate long outputs for display
                display_result = tool_result[:500] + "..." if len(tool_result) > 500 else tool_result
                print(f"Tool Output: {display_result}")
                
                # 4. Feed back to model
                current_input = f"Observation: {tool_result}"
                
            else:
                # Just text/thought, maybe asking for clarification or just thinking
                # If it didn't call a tool or give a final answer, we prompt it to continue
                current_input = "Please continue. If you need to use a tool, specify Action: tool_name(args). If done, say Final Answer: ..."
                
        if step_count >= self.config.agent.max_steps:
            print("\n--- Max Steps Reached ---")

if __name__ == "__main__":
    # Simple test
    agent = KaggleExperimentAssistantAgent()
    # agent.run_workflow("Test run")
