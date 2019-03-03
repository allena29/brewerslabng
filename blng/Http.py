import http.server
import socketserver
import threading
import blng.LogHandler as LogHandler


class HttpHandler(http.server.SimpleHTTPRequestHandler):
    pass


class Http:

    HTTP_PORT = 4998
    HTTP_ADDRESS = "0.0.0.0"

    def __init__(self, http_port=0, log_component=''):
        self.log = LogHandler.LogHandler(log_component + 'Http')
        if http_port:
            self.HTTP_PORT = http_port

    def http_callback_post(self, path, post):
        print('http_callback_post not redefined')

    def http_callback_get(self, path):
        print('http_callback_get not redefined')

    def serve(self):
        self.log.info('Attempting to bind %s:%s' % (self.HTTP_ADDRESS, self.HTTP_PORT))
        self.http_server = socketserver.TCPServer((self.HTTP_ADDRESS, self.HTTP_PORT), HttpHandler)
        self.http_server_thread = threading.Thread(target=self.http_server.serve_forever)
        self.http_server_thread.daemon = True
        self.http_server_thread.start()

        self.http_server.RequestHandlerClass.callback_POST = self.http_callback_post
        self.http_server.RequestHandlerClass.callback_GET = self.http_callback_get

        def do_POST(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()

            content_len = int(self.headers.get('content-length', 0))
            post_body = self.rfile.read(content_len)
            print('post %s %s' % (content_len, post_body))
            self.callback_POST(self.path, post_body)
        #    self.http_post_callback(self.path, post_body)

        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()

            self.callback_GET(self.path)

        self.http_server.RequestHandlerClass.do_POST = do_POST
        self.http_server.RequestHandlerClass.do_GET = do_GET

    def end_serve(self):
        self.http_server.shutdown()
        self.http_server.server_close()
