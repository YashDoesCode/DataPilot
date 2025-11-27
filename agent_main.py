"""
Main entry point for the Kaggle Experiment Assistant Agent (KEAA).

This script allows users to run the agent from the command line or import functions
for use in a Jupyter/Kaggle notebook.
"""

import argparse
import os
import sys
from agent_core import KaggleExperimentAssistantAgent
from config import default_config

def run_agent_session(goal: str, data_path: str = None, offline: bool = False):
    """
    Runs a full agent session with the given goal.
    
    Args:
        goal: The user's high-level goal.
        data_path: Optional path to a specific dataset to focus on.
        offline: If True, forces the agent to run in offline/mock mode.
    """
    # Update config based on arguments
    if offline:
        default_config.kaggle.offline_mode = True
        
    if data_path:
        # Append data path info to the goal
        goal = f"{goal} (Focus on data at: {data_path})"
        
    print(f"Initializing Kaggle Experiment Assistant Agent...")
    if default_config.kaggle.offline_mode:
        print("Mode: OFFLINE (Mock responses)")
    else:
        print("Mode: ONLINE (Gemini 2.5 Pro)")
        
    agent = KaggleExperimentAssistantAgent()
    agent.run_workflow(goal)

def main():
    """
    CLI entry point.
    """
    parser = argparse.ArgumentParser(description="Kaggle Experiment Assistant Agent (KEAA)")
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
