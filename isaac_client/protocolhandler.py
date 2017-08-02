from .websockethandler import WebSocketHandler, websocket
import thread
from base64 import decodestring

from IPython import display


class ProtocolHandler(WebSocketHandler):
    """Handles Send and Receive Events in the ISAAC Protocol

    This is done via the kernel, so expect the most indirect way to get your
    image (but also the most reliable in case you are tunneling your notebook).
    """
    def __init__(self, enable_trace=False):
        """..."""
        websocket.enableTrace(enable_trace)
        pass

    def run_async(self):
        self.wsh = WebSocketHandler(self.message_handler, "149.220.62.186")
        # TODO this is not Python 3 compatible
        thread.start_new_thread(self.wsh.run_forever, ())
        #self.wsh.run_forever()

    def message_handler(self, args):
        #print("ISAAC Message Handler")

        if args["type"] == "hello":
            self.hello_handler(args)
        if args["type"] == "register":
            self.register_handler(args)
        if args["type"] == "period":
            self.period_handler(args)
        if args["type"] == "exit":
            self.exit_handler(args)

    def hello_handler(self, payload):
        """Response on connect to server: lists connected visualizations"""
        print("Hello received:")
        print("  Server name: {}".format(payload["name"]))
        print("  Available streams: {}".format(payload["streams"]))

    def register_handler(self, payload):
        """A new visualization registered at the server"""
        print("Register received:")
        print("  Visualization: {}".format(payload["id"]))
        # TODO check protocol match
        protocol = payload["protocol"]
        print("  Protocol version: {}.{}".format(protocol[0], protocol[1]))
        print("  Sources:")
        for source in payload["sources"]:
            print(source)

    def period_handler(self, payload):
        """A new iteration from the visualization arrived!"""
        #print("Period received: {}".format(payload["meta nr"]))
        image_base64 = payload["payload"]
        # throw away base64 prefix
        prefix = "data:image/jpeg;base64,"
        image_base64 = image_base64[len(prefix):]
        # fix missing padding
        missing_padding = len(image_base64) % 4
        if missing_padding != 0:
            image_base64 += b'='* (4 - missing_padding)

        image_jpg = decodestring(image_base64)

        # don't try this in Firefox v52, use Chromium or something fast
        display.clear_output(wait=True)
        image_notebook = display.Image(image_base64, embed=True)
        display.display(image_notebook)
        
        #display.display(display.HTML('<img src="{}" style="display:inline;margin:1px" />'.format(prefix + image_base64)))

        #image_name = "received_{}.jpg".format(payload["meta nr"])
        #print("Write: {}".format(image_name))
        #with open(image_name, "wb") as fh:
        #    fh.write(image_jpg)

    def exit_handler(self, payload):
        """The visualization exited!"""
        #print("Exit received!")

    def send_observe(self, observe_id, stream=0, dropable=False):
        """Register to receive 'period' messages from a visualization

        Parameters
        ----------
        observe_id: unsigned integer
            The id of the visualization to observe.
        stream: unsigned integer
            Number of the stream to get (JPEG, RDP,...).
        dropable: bool
            If True: it is okay to drop 'period' updates on slow connections.
        """
        #print("Sending observe!")
        d = {
            'type': 'observe',
            'observe id': observe_id,
            'stream': stream,
            'dropable': dropable
        }
        self.wsh.send_message(d)

    def send_feedback(self, args):
        """adjust variables of the visualization"""
        #print("Send feedback to visualization!")
        d = {
            'type': 'feedback'
        }
        d.update(args)
        self.wsh.send_message(d)

    def send_stop(self, observe_id):
        """disconnect from a visualization: stop getting 'period' messages from it"""
        #print("Stop receiving updates from a visualization {}".format(observe_id))
        d = {
            'type': 'stop',
            'observe id': observe_id
        }
        self.wsh.send_message(d)

    def send_closed(self):
        """disconnect from the isaac server"""
        #print("Disconnecting from server!")
        d = {
            'type': 'closed'
        }
        self.wsh.send_message(d)


if __name__ == "__main__":
    import time

    app = ISAACHandler()
    app.run_async()
    time.sleep(2)
    # testing: blindly connect to the first available visualization
    app.send_observe(0, dropable=True)
    time.sleep(200)

