# redis2websocket

redis2websocket is simple microservice app to send (backend-to-frontend, one way) instant signals from backend to frontend web applications running in browser. redis2websocket handles CORS configuration and authentication mechanism for different *room-spaces*.

Example usages:
- ecommerce website may update prices and stock information for all visitors in realtime, without need to refresh. And logged-in customers can see realtime status of their orders. 
- social network may show user if someone is writing new comment right now and display comment when it will be sent
- backend may update frontend about status of long-running requests, such as 'build is N% ready', 'deploying'

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

## redis2websocket vs Flask-SocketIO
redis2websocket is based on [Flask](flask.palletsprojects.com/), [Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO) and [eventlet](https://eventlet.net/). 

Using Flask-SocketIO as server requires to integrate application with Flask and with async webserver with websocket feature such as eventlet. This maybe not very good and not very simple if you use other framework and webserver. Witch redis2websocket, application use Flask-SocketIO in much more simple way.

Also, redis2websocket provides easy authentication mechanism, and you can use one redis2websocket service for many applications.

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
If you want to adjust CORS or ADDRESS settings, edit /etc/default/redis2websocket and restart service.

If you want to run manually from shell:
~~~
# specify default parameters
redis2websocket.py -a 0.0.0.0:8899 --cors http://localhost:7788
~~~

## Authentication and room-spaces
Room name optionally may have format roomspace::roomname (separated by '::'). When client wants to join such room it must provide secret matching redis key r2ws::room_secret::*roomspace*. If secrets aren't match, join request is ignored. All rooms in same roomspace shares same secret.  Backend must set this key and pass secret to frontend.

Rooms without '::' in name, are public, anyone can join it. They are not suited to send any sensitive info.

## Emitting messages over HTTP(s)
It's possible to emit messages from any sources (any programming languages, even from PHP. really.) using HTTP interface. Here is simple example how to emit websocket events right from shell using curl.

HTTP emitting requres secret, like:
~~~
./redis2websocket.py --secret 123
~~~

or set `SECRET=123` in /etc/default/redis2websocket

JSON file `x.json`:
~~~
{
	"event": "update",
	"room": "time",
	"data": {
		"time": 111111
	},
	"namespace": null,
	"secret": "123"
}
~~~

command:
~~~
curl -d @x.json -H "Content-Type: application/json" -X POST http://localhost:8899/emit
~~~

You may run `time.py` example (see below) and execute this curl statement, it will send time 111111 and it will be displayed in browser for short time (less then 1s) until overwritten by next update.


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

