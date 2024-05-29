from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)
socketio = SocketIO(app)

log_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log():
    try:
        guid = request.json.get('guid')
        title = request.json.get('title')
        message = {}
        for item in request.json.keys():
            if item == "guid" or item == "title":
                continue
            message[item] = str(request.json[item])
        
        if guid not in log_data:
            log_data[guid] = []
        log_data[guid].append((title, message))
        tree_data = TreeData(log_data)
        tree_data_json = json.dumps(tree_data)
        socketio.emit('new_log', tree_data_json)
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def TreeData(log_data):
    tree_data = []
    guids = list(log_data.keys())[:]
    for guid in log_data.keys():
        guid_node = {
            "text": guid,
            "state": {"opened": guid == guids[-1]},
            "children": []
        }
        for title, messages in log_data[guid]:
            child_html = "<div>"
            for preceding_text, copyable_text in messages.items():
                child_html += f"""
                    <p>{preceding_text}</p>
                    <div class='text-block' id='{guid}-{title}-{preceding_text}'>
                        <button class='copy-btn' onclick="copyToClipboard('{guid}-{title}-{preceding_text}')">Copy</button>
                        <pre>{copyable_text}</pre>
                    </div>
                """
            child_html += "</div>"
            child_node = {
                "text": title,
                "li_attr": {"class": "custom-node", "data-html": child_html},
                "a_attr": {"href": "#"}
            }
            guid_node["children"].append(child_node)
        tree_data.append(guid_node)
    return tree_data

@socketio.on('connect')
def handle_connect():
    tree_data = TreeData(log_data)
    tree_data_json = json.dumps(tree_data)
    emit('initial_logs', tree_data_json)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)
