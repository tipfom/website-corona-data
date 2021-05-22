from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from corona.data import get_overview_dataset, get_detail_dataset

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        splitted = parsed_path.path.split("/")

        if len(splitted) == 2:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if splitted[1] == "":
                self.wfile.write(get_overview_dataset())
            else:
                self.wfile.write(get_detail_dataset(splitted[1]))
        else:
            self.send_response(400)
            self.end_headers()

