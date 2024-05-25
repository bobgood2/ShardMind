from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import webbrowser
from threading import Timer

app = Flask(__name__)
socketio = SocketIO(app)

log_data = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log():
    message = request.json.get('message')
    log_entry = {"id": len(log_data) + 1, "parent": "#", "text": message}
    log_data.append(log_entry)
    socketio.emit('new_log', log_entry, broadcast=True)
    return '', 204

@socketio.on('connect')
def handle_connect():
    emit('initial_logs', log_data)

def open_browser():
    webbrowser.open_new('http://localhost:8080/')

if __name__ == '__main__':
    Timer(1, open_browser).start()  # Open the browser after a dela
    socketio.run(app, debug=True, port=8080)
