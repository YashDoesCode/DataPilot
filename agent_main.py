import argparse
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from agent_core import KaggleExperimentAssistantAgent
from config import default_config

def run_agent_session(goal: str, data_path: str = None, offline: bool = False):
    if offline:
        default_config.kaggle.offline_mode = True
        
    if data_path:
        goal = f"{goal} (Focus on data at: {data_path})"
        
    print(f"Initializing DataPilot...")
    if default_config.kaggle.offline_mode:
        print("Mode: OFFLINE (Mock responses)")
    else:
        print("Mode: ONLINE (Gemini 2.5 Pro)")
        
    agent = KaggleExperimentAssistantAgent()
    agent.run_workflow(goal)

def main():
    parser = argparse.ArgumentParser(description="DataPilot - Autopilot for Data Science")
    parser.add_argument("--goal", type=str, help="The goal for the agent (e.g., 'Build a baseline for Titanic').")
    parser.add_argument("--data", type=str, help="Path to the dataset (optional).")
    parser.add_argument("--offline", action="store_true", help="Run in offline/mock mode.")
    parser.add_argument("--interactive", action="store_true", help="Start an interactive session.")
    
    args = parser.parse_args()
    
    if args.interactive:
        print("--- Interactive Mode ---")
        goal = input("Enter your goal: ")
        run_agent_session(goal, args.data, args.offline)
    elif args.goal:
        run_agent_session(args.goal, args.data, args.offline)
    else:
        parser.print_help()
        print("\nExample usage:")
        print("  python agent_main.py --goal 'Analyze the housing prices dataset' --offline")

if __name__ == "__main__":
    main()
