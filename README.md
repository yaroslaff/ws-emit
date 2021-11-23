# redis2websocket

redis2websocket is simple microservice app to send (one way) instant signals from backend to frontend web applications running in browser. redis2websocket handles CORS configuration and authentication mechanism for different *room-spaces*.

For example: online shop may update prices and stock information for all visitors in realtime, without need to refresh. And logged-in customers can see realtime status of their orders. 

redis2websocket is isolated microservice, running as separate process, so it does not require any integration and compatibility with your application.

redis2websocket is based on [Flask-SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO) and sending message is as simple as in any other flask-socketio application:

~~~python3
    from flask_socketio import SocketIO
    socketio = SocketIO(message_queue='redis://')

    while True:

        data = {
            'time': int(time.time())
        }
        socketio.emit('update', data, room='time')
~~~

## Authentication and room-spaces
Room name optionally may have format roomspace::roomname (separated by '::'). When client wants to join such room it must provide secret matching redis key r2ws::room_secret::*roomspace*. If secrets aren't match, join request is ignored. All rooms in same roomspace shares same secret.  Backend must set this key and pass secret to frontend.

Rooms without '::' in name, are public, anyone can join it. They are not suited to send any sensitive info.

## Examples

### time
Time is simplest example. No authentication at all.

Start `./redis2websocket.py` in one console. Start `example/time.py` in other console. Navigate browser to http://localhost:7788/ . You will see current system unixtime, it will update every second.

### dir2web
Dir2web is more complex example with authentication and room-spaces.

Create test web directory, e.g. `mkdir /tmp/r2ws`
Start `./redis2websocket.py` in one console. Start `example/time.py` in other console. 


### redis pub/sub channels
~~~
PUBSUB CHANNELS
PUBSUB NUMSUB flask-socketio
SUBSCRIBE flask-socketio
~~~