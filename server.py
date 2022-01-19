import asyncio
import os
import json
import time
import websockets
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from threading import Thread

mimetypes = {
    'html': 'text/html',
    'css': 'text/css',
    'js': 'application/javascript',
    '': 'text/plain',
}

PROGRAM_DIR = os.path.dirname(os.path.realpath(__file__))
messages = {}
websocket_connections = {}
timeout = 15000  # timeout - same as in script.js
SENDER_KEY = "user"
RECIPIENT_KEY = "stranger"
MODE_KEY = "mode"
MESSAGE_KEY = "message"

CONNECT = "CONNECT"
DISCONNECT = "DISCONNECT"


def milliseconds() -> int:
    return int(round(time.time() * 1000))


class RequestHandler(BaseHTTPRequestHandler):  # function for handling requests

    def do_GET(self):  # handle GET request

        request_path = self.path  # request path
        print("GET " + request_path)

        request_path = request_path.replace("../", "/")

        if request_path == "/":  # ROOT PATH
            self.send_file("frontend/html/index.html")

        elif request_path.startswith("/html/") and request_path.endswith(".html"):  # HTML
            filename = os.path.basename(request_path)
            self.send_file("frontend/html/" + filename)

        elif request_path.startswith("/css/") and request_path.endswith(".css"):  # CSS
            filename = os.path.basename(request_path)
            self.send_file("frontend/css/" + filename)

        elif request_path.startswith("/js/") and request_path.endswith(".js"):  # JS
            filename = os.path.basename(request_path)
            self.send_file("frontend/js/" + filename)

        elif request_path == "/get_msg":  # for sending messages to client
            request_info = self.headers.get('info')  # get json data from header saved under info
            print("Request info JSON: " + request_info)

            user, stranger, polling_mode = parse_message_metadata(request_info)  # parse nickname and stranger nickname from JSON

            start = milliseconds()  # actual millis (unix time)
            leave = 0

            # long polling loop
            while leave != 1 and milliseconds() - start < timeout - 100:

                for sender, recipient in messages:
                    if sender == stranger and user == recipient:
                        message = messages[(sender, recipient)]

                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(message)
                        self.wfile.write(str.encode('\n'))

                        del messages[(sender, recipient)]  # remove this msg from list because we found correct client

                        leave = 1  # leave while loop
                        break  # leave this for loop

                if polling_mode == "POLL":
                    break

                time.sleep(0.2)  # for lowering CPU consumption

            if leave == 0:  # no data for client
                # print(f'{user}\'S {polling_mode} ENDED WITH NO DATA')
                self.send_response(204)
                self.send_header("Content-type", "text/plain")
                self.end_headers()

        else:  # ERROR 404
            self.send_not_found()

    def do_POST(self):  # handle POST request
        request_path = self.path  # request path

        print("POST " + request_path)

        if request_path == "/submit_msg":  # new message from client
            content_length = self.headers.get('content-length')  # get length of request body
            request_body = self.rfile.read(int(content_length))  # get request body
            request_info = self.headers.get('info')  # get info JSON from header

            print("Request info JSON: " + request_info)

            sender, recipient, _ = parse_message_metadata(request_info)  # parse nickname and stranger nickname from JSON

            messages[(sender, recipient)] = request_body

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(str.encode("OK"))

        else:  # ERROR 404
            self.send_not_found()

    do_PUT = do_POST
    do_DELETE = do_GET

    def send_file(self, filename):  # for sending file to client
        try:
            mimetype = get_mimetype(filename)  # get filename with path and mimetype

            if filename is not None and mimetype is not None:  # check if convert file path was successful
                full_path = PROGRAM_DIR + os.sep + filename  # get full path to file
                try:
                    file = open(full_path)  # try to open file

                    self.send_response(200)
                    self.send_header('Content-type', mimetype)
                    self.end_headers()
                    self.wfile.write(str.encode(file.read()))  # read file and write it to the client
                    file.close()  # close file

                except OSError:
                    self.send_not_found()

            else:
                self.send_not_found()

        except IOError:
            self.send_not_found()

    def send_not_found(self):
        self.send_error(404, 'File not found: %s' % self.path)


def parse_message_metadata(message):  # function for parsing nickname and stranger nickname from JSON
    data = json.loads(message)
    return data[SENDER_KEY], data[RECIPIENT_KEY], data[MODE_KEY]


def get_mimetype(filename):  # function for getting mimetype
    try:
        name, ext = os.path.splitext(filename)  # get extension
        try:
            return mimetypes[ext.replace('.', '')]  # try get mimetype
        except:
            return mimetypes['']
    except:
        return 'text/plain'


async def websocket_handler(websocket):
    sender = await websocket.recv()
    sender = json.loads(sender)[SENDER_KEY]

    print("SENDER " + sender)
    websocket_connections[websocket] = sender

    while True:
        message = await websocket.recv()
        _, message_content = process_websocket_message(message)
        print("MESSAGE CONTENT " + message_content)
        # if message is None:
        #     their_name = websocket_connections[websocket]
        #     del websocket_connections[websocket]
        #     print('Client closed connection', websocket)
        #     for client, _ in websocket_connections.items():
        #         await client.send(their_name + ' has left the chat')
        #     break

        # Send message to all clients
        for client, _ in websocket_connections.items():
            print(f'Sending to {client}')
            await client.send(message_content)


def process_websocket_message(message) -> (str, str):
    data = json.loads(message)
    print(data)
    return data[SENDER_KEY], data[MESSAGE_KEY]


async def run_WB_server():
    async with websockets.serve(websocket_handler, "localhost", 8080):
        await asyncio.Future()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def run_HTTP_server():
    port = 8008
    server = ThreadedHTTPServer(('', 8008), RequestHandler)
    print('Listening on localhost:%s' % port)

    try:
        server.serve_forever()

    except KeyboardInterrupt:  # handle CTRL+C
        print('^C received, shutting down server')
        server.shutdown()
        print("Closing server")
        server.server_close()


if __name__ == "__main__":
    Thread(target=run_HTTP_server).start()
    Thread(target=asyncio.run(run_WB_server())).start()
