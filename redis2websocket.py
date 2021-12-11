#!/usr/bin/env python3

import os
import argparse
import secrets
import logging

import eventlet

from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

eventlet.monkey_patch()
import redis

async_mode = None

app = Flask(__name__)
socketio = SocketIO()

# redis
r = None


#
# flask submit
#
def emit():
    event = request.json.get('event')
    room = request.json.get('room')
    data = request.json.get('data')
    namespace = request.json.get('namespace')
    socketio.emit(event, data, room=room, namespace=namespace)

    return 'OK\n'

#
# Websocket methods
#
@socketio.event
def connect():
    pass

@socketio.on('disconnect')
def test_disconnect():
    pass

@socketio.event
def join(message):
    log.debug(f"Join room: {message['room']!r} sid: {request.sid!r}")



    if '::' in message['room']:
        roomspace = message['room'].split('::', 1)[0]
        if not message.get('secret'):
            log.debug('No secret in request')
            return
        
        required_secret = r.get('r2ws::room_secret::' + roomspace)
        if not required_secret:
            log.debug(f'required secret not set in redis for {roomspace}')
            return

        if message.get('secret') != required_secret:
            log.debug(f'failed secret for room {message["room"]!r}')
            return 
    print("Join", message['room'])
    join_room(message['room'])

@socketio.event
def leave(message):
    log.debug(f"leave room: {message['room']!r} sid: {request.sid!r}")
    leave_room(message['room'])


def main():

    global log, args, r

    def_redis = os.getenv('REDIS') or 'redis://localhost:6379/0'
    def_address = os.getenv('ADDRESS') or '0.0.0.0:8899'
    def_cors = [os.getenv('CORS', 'http://localhost:7788')]
    def_secret = os.getenv('SECRET')
    def_flask_secret = os.getenv('FLASK_SECRET') or secrets.token_urlsafe(32)

    parser = argparse.ArgumentParser(description='Redis-to-websocket interface')
    parser.add_argument('-v', dest='verbose', action='store_true',
        default=False, help='verbose mode')
    parser.add_argument('--redis', default=def_redis,
        help=f'redis URL def: {def_redis}')
    parser.add_argument('-a', '--address', default=def_address,
        help=f'bind to this Address def: {def_address}')
    parser.add_argument('--cors', default=def_cors, nargs='+',
        help=f'CORS url (without training slash), can repeat or "*". def: {def_cors}')
    parser.add_argument('--secret', default=def_secret, 
        help=f'Secret to submit messages over HTTP')
    parser.add_argument('--flask-secret', default=def_flask_secret, 
        help=f'Flask app secret (any string). Omit to use auto-generated random string')

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

    if '*' in args.cors:
        cors = '*'
    else:
        cors = list()
        for c in args.cors:
            cors.extend(c.split(' '))

    log.info(f'Redis2websocket started on {args.address} cors: {cors}')


    
    app.config['SECRET_KEY'] = args.secret

    r = redis.Redis.from_url(args.redis, decode_responses=True)

    socketio.init_app(app, async_mode=async_mode, cors_allowed_origins=cors, 
        message_queue=args.redis, logger=False, engineio_logger=False)

    if args.secret:
        print("Enable HTTP emitting with secret")
        app.add_url_rule('/emit', methods=['POST'], view_func=emit)
    
    addr = args.address.split(':')

    eventlet.wsgi.server(eventlet.listen((addr[0], int(addr[1]))), app, debug=False)

main()
