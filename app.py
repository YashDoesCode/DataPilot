import os
import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

from agent_core import KaggleExperimentAssistantAgent

app = Flask(__name__, static_folder='static', template_folder='static')

agent = KaggleExperimentAssistantAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        response_text = agent._call_gemini(user_message)
        
        msg_type, content = agent._parse_response(response_text)
        
        tool_call = None
        final_response = ""
        
        if msg_type == "TOOL":
            tool_name, args_str = content
            tool_call = {"name": tool_name, "args": args_str}
            
            tool_result = agent._execute_tool(tool_name, args_str)
            
            final_response = f"Executing {tool_name}...\nOutput: {tool_result}"
            
            # Feed back to agent (simplified for single turn UI, ideally loop)
            # For now, we just show the tool result.
            
        elif msg_type == "FINAL":
            final_response = content
        else:
            final_response = str(content)
            
        return jsonify({
            "response": final_response,
            "tool_call": tool_call
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/experiments', methods=['GET'])
def get_experiments():
    return jsonify([
        {"id": 101, "name": "Titanic Baseline", "status": "Completed"},
        {"id": 102, "name": "Housing Prices XGBoost", "status": "Running"}
    ])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
