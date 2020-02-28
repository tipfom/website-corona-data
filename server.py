from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json

PROTOCOL_VERSION = "0.1"

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        post_parsed_content = json.loads(post_body)
        if post_parsed_content["password"] == "defg":
            self.send_response(200)
        else:
            self.send_response(401)
            
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:4200')
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        
        #self.wfile.write(json.dumps(response))

        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\n",
                str(self.path), str(self.headers))

    def do_OPTIONS(self):           
        self.send_response(200)       
        self.send_header('Access-Control-Allow-Origin', 'http://localhost:4200')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "x-api-key,Content-Type")
        self.end_headers()
        logging.info("OPTIONS request,\nPath: %s\nHeaders:\n%s\n\n",
                str(self.path), str(self.headers))

def run(server_class=HTTPServer, handler_class=RequestHandler, port=5764):
    logging.basicConfig(level=logging.INFO)
    server_address = ('localhost', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


run()
