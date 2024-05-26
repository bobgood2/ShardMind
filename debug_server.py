from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import threading

app = Flask(__name__)
socketio = SocketIO(app)

log_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log():
    try:
        print("got log")
        message = request.json.get('message')
        print(message)
        log_entry = {"id": str(len(log_data) + 1), "parent": "#", "text": str(message)}  # Ensure id is a string and text is a string
        log_data.append(log_entry)
        socketio.emit('new_log', log_data)
        print(f"emitted {log_data}")
        return '', 204
    except Exception as e:
        print(f"exception {e}")
        return jsonify({"error": str(e)}), 500  # Ensure that a response is returned in case of an exception

@socketio.on('connect')
def handle_connect():
    emit('initial_logs', log_data)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)
