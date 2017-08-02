import websocket
import json
from base64 import decodestring

from IPython import display


class WebSocketHandler:
    """Handles the low level websocket protocol to ISAAC server"""

    def __init__(self, msg_handler=None, ip="127.0.0.1", port=2459):
        """connect to an ISAAC server service"""
        self.ws = websocket.WebSocketApp(
            'ws://{}:{}'.format(ip, port),
            subprotocols=['isaac-json-protocol'],
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close
        )
        self.ws.on_open = self.on_open
        self.ws.msg_handler = msg_handler

    def run_forever(self):
        print("WebSocketHandler: Start run!")
        self.ws.run_forever()

    @staticmethod
    def on_message(ws, message):
        #print("WebSocketHandler: Message Handler")

        # this is potentially dangerous
        d = json.loads(message)

        if ws.msg_handler is not None:
            ws.msg_handler(d)
        else:
            print("WebSocketHandler: No message handler registered!")

    @staticmethod
    def on_error(ws, error):
        print("Error: ")
        print(error)

    @staticmethod
    def on_close(ws):
        print("WebSocketHandler: closed")

    @staticmethod
    def on_open(ws):
        pass

    def send_message(self, args):
        json_args = json.dumps(args)
        #print("WebSocketHandler: Send")
        #print(json_args)
        self.ws.send(json_args)

