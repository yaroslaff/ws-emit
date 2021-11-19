#!/usr/bin/env python3

import os
import json
import time
import argparse
import secrets
import logging

import eventlet

from threading import Lock

from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

eventlet.monkey_patch()
import redis

async_mode = None

app = Flask(__name__)
#socketio = SocketIO(app, async_mode=async_mode)
socketio = SocketIO()

thread = None
thread_lock = Lock()

address = None


#
# Flask app views
#
# views here are without route decorators. routes are added only if --demo
#
def index():
    print(f"<{os.getpid()}> index")
    return render_template('index.html', async_mode=socketio.async_mode)

def catch_all(path):
    root = os.path.realpath(args.demo)

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
    

def list():
    log.debug(f"list {args.demo}")
    return json.dumps(os.listdir(args.demo), indent=4)

#
# Websocket methods
#
@socketio.event
def connect():
    print(f"<{os.getpid()}> connected", request.sid)
    return


    global thread
    with thread_lock:
        if thread is None:
            print(f"<{os.getpid()}> start bg")
            thread = socketio.start_background_task(background_thread)
            print(f"<{os.getpid()}> started {thread}")
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    log.info(f'<{os.getpid()}> Client disconnected {request.sid}')

@socketio.event
def my_ping():
    # log.debug("got ping")
    emit('my_pong')

@socketio.event
def watch(message):
    log.debug(f"watch room: {message} sid: {request.sid}")
    join_room(message['room'])

@socketio.event
def stopwatch(message):
    log.debug(f"stopwatch room: {message} sid: {request.sid}")
    leave_room(message['room'])


#
# Background thread
#

def background_thread():
    r = redis.Redis.from_url(args.redis)
    print(f"<{os.getpid()}> background thread started")

    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        event_str = r.lpop(args.queue)

        if event_str:
            log.debug(f"{int(time.time())} request: {event_str}")
            # request is something
            event = json.loads(event_str)
            log.debug(json.dumps(event, indent=4))

        socketio.sleep(args.sleep)
        count += 1
        # socketio.emit('my_response',
        #              {'data': 'Server generated event', 'count': count})


def main():

    global log, args

    def_redis = os.getenv('REDIS') or 'redis://localhost:6379/0'
    def_queue = 'redis2websocket'
    def_event = 'r2ws_event'
    def_address = os.getenv('ADDRESS') or '0.0.0.0:8899'
    def_sleep = '0.5'
    def_cors = ['http://localhost:7788']
    def_secret = os.getenv('SECRET') or secrets.token_urlsafe(32)

    parser = argparse.ArgumentParser(description='Redis-to-websocket interface')
    parser.add_argument('-v', dest='verbose', action='store_true',
        default=False, help='verbose mode')
    parser.add_argument('-n', dest='db', type=int, default=0,
        help='Redis database number (0 default)')
    parser.add_argument('--redis', default=def_redis,
        help=f'redis URL def: {def_redis}')
    parser.add_argument('-e', '--event', default=def_event,
        help=f'websocket event name def: {def_event}')
    parser.add_argument('-q', '--queue', default=def_queue,
        help=f'queue (list) key name def: {def_queue}')
    parser.add_argument('-a', '--address', default=def_address,
        help=f'bind to this Address def: {def_address}')
    parser.add_argument('-s', '--sleep', default=def_sleep, type=float,
        help=f'redis polling period def: {def_sleep}')
    parser.add_argument('--cors', default=def_cors, nargs='+',
        help=f'CORS url (without training slash), can repeat or "*". def: {def_cors}')
    parser.add_argument('--secret', default=def_secret, 
        help=f'Flask app secret (any string). Omit to use auto-generated random string')
    parser.add_argument('--demo', default=None, nargs='?', metavar='PATH',
        const='.',
        help=f'enable demo mode')

    args = parser.parse_args()



    logging.basicConfig(
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

    log = logging.getLogger()

    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.debug('Verbose mode')
        # err = logging.StreamHandler(sys.stderr)
        # log.addHandler(err)

    log.info('Redis2websocket started')

    if args.demo:
        print(f"demo mode, serve path {args.demo}")
        app.add_url_rule("/", view_func=index)
        app.add_url_rule("/_list", view_func=list)
        app.add_url_rule('/<path:path>', view_func=catch_all)


    if '*' in args.cors:
        args.cors = '*'
    
    print("use secret:", args.secret)
    app.config['SECRET_KEY'] = args.secret


    socketio.init_app(app, async_mode=async_mode, cors_allowed_origins=args.cors, message_queue='redis://', 
        namespace='/test', logger=True, engineio_logger=True)

    addr = args.address.split(':')
    
    addr = args.address.split(':')
    #app.run(host=addr[0], port=int(addr[1]), debug=True)

    log.debug("start eventlet")
    eventlet.wsgi.server(eventlet.listen((addr[0], int(addr[1]))), app, debug=True)

main()
