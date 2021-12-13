#!/usr/bin/env python3

import redis
import time
import os
import argparse
import threading
from flask_socketio import SocketIO

from flask import Flask, render_template, session, request, \
    copy_current_request_context

args = None
r = None
th = None

app = Flask(__name__)

@app.route('/')
def index():
    host = request.host.split(':')[0]    
    return render_template('time.html', scheme=request.scheme, host=host)

def sysinfo():

    socketio = SocketIO(message_queue=args.redis)

    while True:

        data = {
            'time': int(time.time())
        }
        socketio.emit('update', data, room='time')
        time.sleep(1)

def main():
    global args, r, th

    def_redis = 'redis://'
    def_path = '/tmp'
    def_address = 'localhost:7788'
    def_redis = os.getenv('REDIS') or 'redis://localhost:6379/0'


    parser = argparse.ArgumentParser(description='time ws-emit demo')
    parser.add_argument('-v', dest='verbose', action='store_true',
        default=False, help='verbose mode')
    parser.add_argument('--redis', default=def_redis,
        help=f'redis URL. Def: {def_redis}')
    parser.add_argument('-a', '--address', default=def_address,
        help=f'bind to this Address. Def: {def_address}')

    args = parser.parse_args()

    r = redis.Redis.from_url(args.redis)

    th = threading.Thread(target=sysinfo, args=())
    th.daemon = True 
    th.start()

    addr = args.address.split(':')
    app.run(host=addr[0], port=int(addr[1]))


main()