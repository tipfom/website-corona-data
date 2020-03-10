import logging
from http.server import HTTPServer
from requesthandler import HTTPRequestHandler
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def run(server_class=ThreadedHTTPServer, handler_class=HTTPRequestHandler, port=5764):
    logging.basicConfig(level=logging.INFO)
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")


run()
