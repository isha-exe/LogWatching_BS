import os
import time
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit
from threading import Thread


app = Flask(__name__)
socketio = SocketIO(app)


LOG_FILE = 'logfile.log'


@app.route('/')
def index():
    return render_template('home.html')


def watch_log():
    with open(LOG_FILE, 'r') as f:
        f.seek(0, os.SEEK_END)
        end_byte = f.tell()
        lines = []
        buffer = bytearray()
        while len(lines) < 10 and end_byte > 0:
            try:
                f.seek(end_byte - 1)
                byte = f.read(1)
                if byte == b'\n':
                    line = buffer.decode('utf-8')[::-1]
                    lines.append(line)
                    buffer = bytearray()
                else:
                    buffer.extend(byte.encode('utf-8'))
                end_byte -= 1
            except ValueError:
                break
        if buffer:
            lines.append(buffer.decode('utf-8')[::-1])
        for line in lines[::-1]:
            socketio.emit('log', {'data': line})
        

def get_last_lines():
    with open(LOG_FILE, 'r') as f:
        f.seek(0, os.SEEK_END)
        end_byte = f.tell()
        lines = []
        buffer = bytearray()
        while len(lines) < 10 and end_byte > 0:
            #if end_byte == 1: break;
            try:
                f.seek(end_byte - 1)
                byte = f.read(1)
                if byte == b'\n':
                    if buffer:
                        line = buffer.decode('utf-8')[::-1]
                        lines.append(line)
                        buffer = bytearray()
                else:
                    buffer.extend(byte.encode('utf-8'))
                end_byte -= 1
            except ValueError:
                break
        print("length" , len(lines))
        if buffer:
            lines.append(buffer.decode('utf-8')[::-1])
        return lines[::-1]
    
@socketio.on('connect')
def handle_connect():
    last_10_lines = get_last_lines()
    for line in last_10_lines:
        print(line)
        socketio.emit('log', {'data': line})
    print('Client connected')
    print(get_last_lines())

with app.app_context():
    thread = Thread(target=watch_log)
    thread.daemon = True
    thread.start()


if __name__ == '__main__':
    socketio.run(app, debug=True)
