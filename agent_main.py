import argparse
from agent_core import KaggleExperimentAssistantAgent
from config import default_config

def run_agent_session(goal: str, data_path: str = None, offline: bool = False):
    if offline: default_config.kaggle.offline_mode = True
    if data_path: goal = f"{goal} (Data: {data_path})"
    print(f"Mode: {'OFFLINE' if default_config.kaggle.offline_mode else 'ONLINE'}")
    KaggleExperimentAssistantAgent().run_workflow(goal)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--goal", type=str)
    p.add_argument("--data", type=str)
    p.add_argument("--offline", action="store_true")
    p.add_argument("--interactive", action="store_true")
    args = p.parse_args()
    
    if args.interactive:
        run_agent_session(input("Goal: "), args.data, args.offline)
    elif args.goal:
        run_agent_session(args.goal, args.data, args.offline)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
