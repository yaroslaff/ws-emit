# WS-Emit

WS-Emit is simple microservice app to send instant messages (websocket events) from backend to frontend web applications running in browser (one way). ws-emit handles CORS configuration and authentication mechanism for different *room-spaces*.

Example usages:
- ecommerce website may update prices, stock and orders information on page in realtime, without need to refresh. 
- social network may show user if someone is writing new comment right now and display comment when it will be submitted
- backend may update frontend about status of long-running requests, such as 'build is N% ready', 'deploying'

WS-Emit benefits:
- Isolated microservice, not requires any integration with your application
- Compatible with application in any programming languages (if they can send HTTP requests or publish data to redis), any frameworks, any application web server 

WS-Emit is based on [Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO) and sending message is as simple as in any other flask-socketio application:

~~~python3
socketio.emit('update', data, room='time')
~~~

or via HTTP interface (see below):
~~~
curl -d @x.json -H "Content-Type: application/json" -X POST http://localhost:8899/emit
~~~

## Screencast
See below for detailed explanation what every example does.

[![ws-emit screencast](https://img.youtube.com/vi/yQCIBFuogg4/0.jpg)](https://www.youtube.com/watch?v=yQCIBFuogg4)

## Installation
~~~
pip3 install ws-emit
~~~
or, install right from github repo:
~~~
pip3 install git+https://github.com/yaroslaff/ws-emit
~~~

If you want to install as systemd service:
~~~
cp /usr/local/ws-emit/contrib/ws-emit /etc/default/
cp /usr/local/ws-emit/contrib/ws-emit.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ws-emit
systemctl start ws-emit
~~~
If you want to adjust CORS, ADDRESS or SECRET settings, edit /etc/default/ws-emit and restart service.

If you want to run manually from shell:
~~~
# specify default parameters
ws-emit.py -a 0.0.0.0:8899 --cors http://localhost:7788 --secret 123
~~~

## Authentication and room-spaces
Room name optionally may have format roomspace::roomname (separated by '::'). When client wants to join such room it must provide secret matching redis key ws-emit::room_secret::*roomspace*. If secrets aren't match, join request is ignored. All rooms in same roomspace shares same secret.  Backend must set this key in redis (e.g. `SET ws-emit::room_secret::myroom MySecret_123`) and pass secret to frontend.

Rooms without '::' in name, are public, anyone can join it. They are not suited to send any sensitive info.

## Emitting messages over HTTP(s)
It's possible to emit messages from any sources (any programming languages, even from PHP or Perl or shell scripts. really.) using HTTP interface. Here is simple example how to emit websocket events right from shell using curl.

HTTP emitting requres secret, like:
~~~
./ws-emit.py --secret MySecret
~~~

or set `SECRET=MySecret` in /etc/default/ws-emit and restart ws-emit service.

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

Start `/usr/local/ws-emit/example/time.py` in console. Navigate browser to http://localhost:7788/. You will see current system unixtime, it will update every second. 

Make sure addresses are exactly matching to CORS value in ws-emit (--cors option or CORS= parameter in /etc/default/ws-emit), http://localhost:7788 (default) and http://127.0.0.1:7788 are different

### dir2web
Dir2web is more complex example with authentication and room-spaces.

Create test web directory, e.g. `mkdir /tmp/ws-emit`.
Start `/usr/local/ws-emit/example/dir2web.py /tmp/ws-emit` in console and open http://localhost:7788 in browser. You will see all files in this directory, if you will create new file (`echo aaa > /tmp/ws-emit/aaa.txt`), it will be immediately listed in browser. You can open file in browser, and if you will change file content  (`echo aaa2 > /tmp/ws-emit/aaa.txt`) it will be immediately updated in browser.

dir2web uses roomspace `dir` and sets access key to this roomspace as redis-key `ws-emit::room_secret::dir`. This key is provided to JS code running in browser, and then JS code send key when join rooms inside this roomspace.

### subspy
Subspy `/usr/local/ws-emit/example/subspy.py` it simple utility to *sniff* traffic in publish/subscribe redis channel.

Example output (from time.py example):
~~~
# /usr/local/ws-emit/example/subspy.py 
All channels: [b'flask-socketio']
INT: 1
{'method': 'emit', 'event': 'update', 'data': {'time': 1639178370}, 'namespace': '/', 'room': 'time', 'skip_sid': None, 'callback': None, 'host_id': 'ce56fbc176624c7e8511a583cd5030a8'}
{'method': 'emit', 'event': 'update', 'data': {'time': 1639178371}, 'namespace': '/', 'room': 'time', 'skip_sid': None, 'callback': None, 'host_id': 'ce56fbc176624c7e8511a583cd5030a8'}
~~~

You may use subspy to generate websocket events in other languages (But messages must be serialized in python [pickle](https://docs.python.org/3/library/pickle.html) format).

