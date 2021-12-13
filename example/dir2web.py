#!/usr/bin/env python3

import redis
import json
import os
import argparse
import inotify.adapters, inotify.constants
import secrets
import signal
import threading
from flask_socketio import SocketIO

from flask import Flask, render_template, session, request, \
    copy_current_request_context

args = None
r = None
th = None
room_secret = None
app = Flask(__name__)



@app.route('/')
def index():
    host = request.host.split(':')[0]    
    return render_template('dir2web.html', scheme=request.scheme, host=host)

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

@app.route('/_secret')
def secret():
    return room_secret


def watch():

    socketio = SocketIO(message_queue=args.redis)
    i = inotify.adapters.Inotify()

    mask = inotify.constants.IN_CLOSE_WRITE | inotify.constants.IN_CREATE | inotify.constants.IN_DELETE
    i.add_watch(args.path, mask=mask)

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        #print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
        #        path, filename, type_names))


        if 'IN_DELETE' in type_names or 'IN_CREATE' in type_names:
            data = {
                'data': 'modified'
            }
            print("Emit rescan")
            socketio.emit('rescan', data, room='dir::_rescan')
        else:                    
            data = {
                'file': filename,
                'data': 'modified'
            }
            print(f"Emit update for file {filename}")
            socketio.emit('update', data, room='dir::'+filename)

def main():
    global args, r, th, room_secret

    def_redis = 'redis://'
    def_path = '/tmp'
    def_address = '0.0.0.0:7788'
    def_redis = os.getenv('REDIS') or 'redis://localhost:6379/0'
    def_secret = secrets.token_urlsafe(32)


    parser = argparse.ArgumentParser(description='dir2web ws-emit demo')
    parser.add_argument('-v', dest='verbose', action='store_true',
        default=False, help='verbose mode')
    parser.add_argument('--redis', default=def_redis,
        help=f'redis URL. Def: {def_redis}')
    parser.add_argument('-a', '--address', default=def_address,
        help=f'bind to this Address. Def: {def_address}')
    parser.add_argument('--secret', default=def_secret, 
        help=f'room secret (def: random)')
    parser.add_argument('path', default=def_path, nargs='?',
        help=f'directory path. Def: {def_path}')

    args = parser.parse_args()

    r = redis.Redis.from_url(args.redis)
    room_secret = args.secret
    r.set('ws-emit::room_secret::dir', room_secret)

    th = threading.Thread(target=watch, args=())
    th.daemon = True 
    th.start()

    addr = args.address.split(':')
    app.run(host=addr[0], port=int(addr[1]))


main()