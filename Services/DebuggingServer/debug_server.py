from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import uuid
from datetime import datetime, timedelta
import traceback

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
        timestamp_str = request.json.get('timestamp')
        time_stamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')

        duration = request.json.get('duration', 0)
        message = {}
        for item in request.json.keys():
            if item == "guid" or item == "title" or item == "timestamp" or item == "duration":
                continue
            message[item] = str(request.json[item])
        
        if guid not in log_data:
            log_data[guid] = []
        log_data[guid].append((title, message, time_stamp, duration))
        tree_data = TreeData(log_data)
        tree_data_json = json.dumps(tree_data)
        socketio.emit('new_log', tree_data_json)
        return '', 204
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def TreeData(log_data):
    try:
        tree_data = []
        guids = list(log_data.keys())[:]
        for guid in log_data.keys():
            guid_node = {
                "text": guid,
                "state": {"opened": guid == guids[-1]},
                "children": []
            }
        
            guid_data=log_data[guid]
            sorted_data = sorted(guid_data, key=lambda x: x[2])
            total_latency=0
            total_header=guid
            if len(sorted_data)>0:
                orig_time = sorted_data[0][2]
                if "query" in sorted_data[0][1]:
                    total_header=sorted_data[0][1]["query"]
            
            for title, messages, start_time, duration in sorted_data:
                latency = (start_time - orig_time).total_seconds()
                total_latency=latency+duration
                header = f"{title}  @{latency} duration:{duration}"
                if duration==0:
                    header = f"{title} start:{latency}"

                grand_child_html = '<div class="custom-content">'
                for preceding_text, copyable_text in messages.items():
                    grand_child_html += f"""
                        <p>{preceding_text}</p>
                        <div class='text-block' id='{guid}-{title}-{preceding_text}'>
                            <button class='copy-btn'  style='padding: 1px 3px; font-size: 12px;' onclick="copyToClipboard('{guid}-{title}-{preceding_text}')">Copy</button>
                            <pre>{copyable_text}</pre>
                        </div>
                    """
                grand_child_html += "</div>"
                grand_child_node = {
                    "text": "Details",
                    "li_attr": {"class": "custom-node", "data-html": grand_child_html},
                    "a_attr": {"href": "#"}
                }
                child_node = {
                    "text": header,
                    "state": {"opened": False},
                    "children": [grand_child_node]
                }
                guid_node["children"].append(child_node)
            guid_node["text"]=f"{total_header} latency:{total_latency}"
            tree_data.append(guid_node)
        return tree_data
    except Exception as e:
        stack_trace = traceback.format_exc()
        print(e)
        print(stack_trace)


@socketio.on('connect')
def handle_connect():
    tree_data = TreeData(log_data)
    tree_data_json = json.dumps(tree_data)
    emit('initial_logs', tree_data_json)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)
