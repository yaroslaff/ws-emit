# redis2websocket

redis2websocket is simple microservice app to send (backend-to-frontend, one way) instant signals from backend to frontend web applications running in browser. redis2websocket handles CORS configuration and authentication mechanism for different *room-spaces*.

For example: online shop may update prices and stock information for all visitors in realtime, without need to refresh. And logged-in customers can see realtime status of their orders. 

redis2websocket is isolated microservice, running as separate process, so it does not require any integration and compatibility with your application.

redis2websocket is based on [Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO) and sending message is as simple as in any other flask-socketio application:

~~~python3
    import time
    from flask_socketio import SocketIO
    socketio = SocketIO(message_queue='redis://')

    while True:

        data = {
            'time': int(time.time())
        }
        socketio.emit('update', data, room='time')
        time.sleep(1)
~~~

## Installation
~~~
pip3 install redis2websocket
~~~
or, install right from github repo:
~~~
pip3 install git+https://github.com/yaroslaff/redis2websocket
~~~

If you want to install as systemd service:
~~~
cp /usr/local/redis2websocket/contrib/redis2websocket /etc/default/
cp /usr/local/redis2websocket/contrib/redis2websocket.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable redis2websocket
systemctl start redis2websocket
~~~

If you want to run manually from shell:
~~~
~~~


## Authentication and room-spaces
Room name optionally may have format roomspace::roomname (separated by '::'). When client wants to join such room it must provide secret matching redis key r2ws::room_secret::*roomspace*. If secrets aren't match, join request is ignored. All rooms in same roomspace shares same secret.  Backend must set this key and pass secret to frontend.

Rooms without '::' in name, are public, anyone can join it. They are not suited to send any sensitive info.

## Examples

### time
Time is simplest example. No authentication at all.

Start `/usr/local/redis2websocket/example/time.py` in console. Navigate browser to http://localhost:7788/. You will see current system unixtime, it will update every second. 

Caveats:
- Make sure addresses are exactly matching to CORS value in redis2websocket, http://localhost:7788 (default) and http://127.0.0.1:7788 are different
- socketio server address (http://localhost:8899) is hardcoded into HTML file (/usr/local/redis2websocket/example/templates/dir2web.html). If you start it not on localhost (e.g. in LXC container), you need to set correct address.

### dir2web
Dir2web is more complex example with authentication and room-spaces.

Create test web directory, e.g. `mkdir /tmp/r2ws`.
Start `/usr/local/redis2websocket/example/dir2web.py /tmp/r2ws` in console and open http://localhost:7788 in browser. You will see all files in this directory, if you will create new file (`echo aaa > /tmp/r2ws/aaa.txt`), it will be immediately listed in browser. You can open file in browser, and if you will change file content  (`echo aaa2 > /tmp/r2ws/aaa.txt`) it will be immediately updated in browser.

dir2web uses roomspace `dir` and sets access key to this roomspace as redis-key `r2ws::room_secret::dir`. This key is provided to JS code running in browser, and then JS code send key when join rooms inside this roomspace.

### subspy
Subspy `/usr/local/redis2websocket/example/dir2web.py` it simple utility to *sniff* traffic in publish/subscribe redis channel.

Example output (from time.py example):
~~~
# /usr/local/redis2websocket/example/subspy.py 
All channels: [b'flask-socketio']
INT: 1
{'method': 'emit', 'event': 'update', 'data': {'time': 1639178370}, 'namespace': '/', 'room': 'time', 'skip_sid': None, 'callback': None, 'host_id': 'ce56fbc176624c7e8511a583cd5030a8'}
{'method': 'emit', 'event': 'update', 'data': {'time': 1639178371}, 'namespace': '/', 'room': 'time', 'skip_sid': None, 'callback': None, 'host_id': 'ce56fbc176624c7e8511a583cd5030a8'}
~~~

You may use subspy to generate websocket events in other languages (But messages must be serialized in python [pickle](https://docs.python.org/3/library/pickle.html) format).

