#!/usr/bin/env python3

import redis
import json
import os
import argparse
import inotify.adapters, inotify.constants
import threading
from flask_socketio import SocketIO

from flask import Flask, render_template, session, request, \
    copy_current_request_context

args = None
r = None

app = Flask(__name__)

@app.route('/')
def index():
    print(f"<{os.getpid()}> index")
    return render_template('index.html')

@app.route('/<path:path>')
def catch_all(path):
    root = os.path.realpath(args.path)

    if '..' in path or '/' in path:
        return "I do not like this request", 403

    filepath = os.path.realpath(os.path.join(root, path))

    if not filepath.startswith(root):
        return "I do not want to send this file", 403

    try:
        with open(filepath) as fh:
            data = fh.read()
    except FileNotFoundError:
        return "no such file", 404
    
    return data
    
@app.route('/_list')
def list():
    print(f"list {args.path}")
    return json.dumps(os.listdir(args.path), indent=4)

def get_redis():

    if args.redis.startswith('/'):
        path = args.redis
        host = None
        port = None
    else:
        host, port = args.redis.split(':')
        path = None

    print(f"connect to unix: {path} network: {host}:{port}")
    return redis.Redis(
        db=args.db,
        unix_socket_path=path, 
        host=host, port=port,
        decode_responses=True)


def watch():

    socketio = SocketIO(message_queue=args.redis)
    i = inotify.adapters.Inotify()

    mask = inotify.constants.IN_CLOSE_WRITE
    i.add_watch('/tmp', mask=mask)

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        #print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
        #      path, filename, type_names))
        data = {
            'room': filename,
            'data': 'modified'
        }
        print(f"emit update for {filename}")
        socketio.emit('update', data, room=filename)
        

def main():
    global args, r

    def_redis = 'redis://'
    def_path = '/tmp'
    def_address = '0.0.0.0:7788'
    def_redis = os.getenv('REDIS') or 'redis://localhost:6379/0'


    parser = argparse.ArgumentParser(description='redis2websocket demo')
    parser.add_argument('-v', dest='verbose', action='store_true',
        default=False, help='verbose mode')
    parser.add_argument('--redis', default=def_redis,
        help=f'redis URL. Def: {def_redis}')
    parser.add_argument('-a', '--address', default=def_address,
        help=f'bind to this Address. Def: {def_address}')
    parser.add_argument('path', default=def_path, nargs='?',
        help=f'directory path. Def: {def_path}')

    args = parser.parse_args()

    r = redis.Redis.from_url(args.redis)
    # watch()

    th = threading.Thread(target=watch, args=())
    th.start()

    addr = args.address.split(':')
    app.run(host=addr[0], port=int(addr[1]))

main()