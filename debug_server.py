from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import threading

app = Flask(__name__)
socketio = SocketIO(app)

log_data = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log():
    try:
        print("got log")
        message = request.json.get('message')
        title = request.json.get('title')
        guid = request.json.get('guid')
        print(message)
        log_entry = {"id": str(len(log_data) + 1), "parent": "#", "text": str(message)}  # Ensure id is a string and text is a string
        if guid not in log_data:
            log_data[guid]=[]
            
        log_data[guid].append((title, str(message)))
        tree_data=TreeData(log_data)
        tree_data_json = json.dumps(tree_data)
        socketio.emit('new_log', tree_data_json)
        print(f"emitted {tree_data_json}")
        return '', 204
    except Exception as e:
        print(f"exception {e}")
        return jsonify({"error": str(e)}), 500  # Ensure that a response is returned in case of an exception

def TreeData(log_data):
    tree_data = []
    guids = list(log_data.keys())[:]
    for guid in log_data.keys():
        guid_node = {}
        guid_node["text"]=guid
        opened = guid==guids[-1]
        guid_node["state"] = {"opened":opened}
        children_list =[]
        for item in log_data[guid]:
            title = item[0]
            message=item[1]
            stub0={"opened":False}
            stub={"text":message, "state":stub0}
            child = {"text":title, "children":[stub]}
            children_list.append(child)
        guid_node["children"]=children_list
        
        tree_data.append(guid_node)
    return tree_data
        
@socketio.on('connect')
def handle_connect():
        tree_data=TreeData(log_data)
        tree_data_json = json.dumps(tree_data)
        print(f"emitted {tree_data_json}")
        emit('initial_logs', tree_data_json)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)
