#!/usr/bin/env python3

import redis
import pickle
import time
import os
import argparse

args = None
r = None
th = None

def main():
    global args, r, th

    def_redis = 'redis://'
    def_path = '/tmp'
    def_address = 'localhost:7788'
    def_redis = os.getenv('REDIS') or 'redis://localhost:6379/0'
    def_channel = "flask-socketio"


    parser = argparse.ArgumentParser(description='ws-emit redis PUBSUB sniffer')
    parser.add_argument('-v', dest='verbose', action='store_true',
        default=False, help='verbose mode')
    parser.add_argument('--redis', default=def_redis,
        help=f'redis URL. Def: {def_redis}')
    parser.add_argument('--channel', default=def_channel,
        help=f'Channel name to spy. Def: {def_channel}')
    
    args = parser.parse_args()

    r = redis.Redis.from_url(args.redis)

    print(f"All channels: {r.pubsub_channels()}")
    p = r.pubsub()
    p.subscribe(args.channel)
    for msg in p.listen():
        if isinstance(msg['data'], int):
            print("INT:", msg['data'])
        else:
            data = pickle.loads(msg['data'])
            print(data)


main()