
from typing import Any
from server import webserver
from websockets.sync.server import serve, Server, ServerConnection
from websockets import Data
import threading
from flask import Flask
import json

clients = []
primary_client = None
def set_primary(client: ServerConnection):
    global primary_client
    if primary_client != None:
        print("primary client already exists")
        return
    primary_client = client
    client.send({"primary": True})

def on_message(client: ServerConnection, message: dict[str, Any]):
    global primary_client
    request = message.get("request")
    if request != None:
        match request:
            case "status":
                if primary_client == None:
                    set_primary(client)
                    return
                client.send({"primary": client == primary_client, "position": (0, 0), "sensor_readings": {"ground1": False, "distance1": 4.5}})
            case "make_not_primary":
                if primary_client == client:
                    primary_client = None
                client.send({"primary": False})
            case "controls":
                print(f"Moved to {message['x']} {message['y']}")
            case "sensitivity":
                print("sens: " + str(message["value"]))

def websocket_handler(client: ServerConnection):
    clients.append(client)
    super_send = client.send
    def extended_send(message, text=False):
        if type(message) == dict:
            super_send(json.dumps(message), text=True)
            return
        super_send(message)
    client.send = extended_send
    global primary_client
    if primary_client == None:
        set_primary(client)
    for message in client:
        try:
            on_message(client, json.loads(message))
        except Exception as e:
           print("Failed to process message: " + str(message))
           print(e.with_traceback)
    clients.remove(client)
    if client == primary_client:
        if len(clients) == 0: return
        set_primary(clients[0])

def start_websocket(app: Flask):
    websocket: Server = serve(websocket_handler, app.config["bind"][0], port=3001)
    setattr(Flask, "_websocket", websocket)
    def start_websocket():
        print("WebSocket listening at: " + str(websocket.socket.getsockname()))
        global clients
        app.config["websocket_clients"] = clients
        app.config["websocket_server"] = websocket
        websocket.serve_forever()
    websocket_thread = threading.Thread(target=start_websocket)
    websocket_thread.daemon = True
    websocket_thread.name = "Robot-Websocket-Thread"
    websocket_thread.start()

bind = ("0.0.0.0", 5000)
def restart(app):
    app.config["bind"] = bind
    if hasattr(Flask, "_websocket"):
        websocket = getattr(Flask, "_websocket")
        websocket.shutdown()
    start_websocket(app)
webserver(restart=restart).run(host=bind[0], port=bind[1], debug=True)