import json
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from agent import DataPilot

load_dotenv()
app = Flask(__name__, static_folder='static', template_folder='static')
agent = DataPilot()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    msg = request.json.get('message')
    if not msg: return jsonify({"error": "No message"}), 400
    
    raw_resp = agent.chat(msg)
    try:
        parsed = json.loads(raw_resp)
        tool_call = None
        response_text = parsed.get("final_answer", "")
        
        if "tool_name" in parsed:
            t_name = parsed["tool_name"]
            t_args = parsed.get("tool_args", [])
            tool_call = {"name": t_name, "args": str(t_args)}
            res = agent.execute_tool(t_name, t_args)
            response_text = f"Executed {t_name}. Result: {res[:200]}..."
            
        return jsonify({"response": response_text, "tool_call": tool_call})
    except: return jsonify({"response": raw_resp})

if __name__ == '__main__': app.run(debug=True, port=5000)
