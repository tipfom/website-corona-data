from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
from random import randrange
import mysql.connector
from urllib.parse import urlparse
from random import randint
import uuid
import base64

PROTOCOL_VERSION = "0.1"

ALLOWED_TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
valid_tokens = []

mysql_host = "tim-nas"  # Rechnername (localhost ist dein eigener Rechner)
mysql_port = 3307
mysql_user = "admin"
mysql_pass = "YNy2*rJAck%DcS^#"
mysql_db = "website_cms"

# Verbindung mit der Datenbank
mysql_conn = mysql.connector.connect(
    host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pass
)
mysql_conn.database = mysql_db
mysql_cursor = mysql_conn.cursor()


def generateToken(length):
    token = ""
    for i in range(length):
        token += ALLOWED_TOKEN_CHARS[randrange(len(ALLOWED_TOKEN_CHARS))]
    return token


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path.startswith("/resource/"):
            splitted = parsed_path.path.split("/")
            if len(splitted) == 3:
                id = base64.urlsafe_b64decode(splitted[2].encode()).hex()
                sql_query = "SELECT type FROM entries WHERE uuid=X'{}'".format(id)
                mysql_cursor.execute(sql_query)
                row = mysql_cursor.fetchone()
                if row != None:
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write((row[0] + "\n").encode())
                    sql_query = "SELECT path FROM resources WHERE entry_uuid=X'{}'".format(
                        id
                    )
                    mysql_cursor.execute(sql_query)
                    for row in mysql_cursor.fetchall():
                        self.wfile.write((row[0] + "\n").encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path.startswith("/login"):
            content_len = int(self.headers.get("Content-Length"))
            post_content = self.rfile.read(content_len)
            post_parsed_content = json.loads(post_content)
            if post_parsed_content["password"] == "defg":
                self.send_response(201)
                new_token = generateToken(20)
                valid_tokens.append(new_token)
                self.send_header("Access-Control-Allow-Origin", "http://localhost:4200")
                self.end_headers()
                self.wfile.write(('{"token":"' + new_token + '"}').encode())
            else:
                self.send_response(401)
                self.send_header("Access-Control-Allow-Origin", "http://localhost:4200")
                self.end_headers()

        elif parsed_path.path.startswith("/resource"):
            content_len = int(self.headers.get("Content-Length"))
            post_content = self.rfile.read(content_len)
            post_parsed_content = json.loads(post_content)
            if valid_tokens.__contains__(post_parsed_content["token"]):
                id = uuid.uuid4()
                sql_query = "INSERT INTO entries (uuid, type) VALUES (X'{}', '{}');".format(
                    id.hex, post_parsed_content["type"]
                )
                mysql_cursor.execute(sql_query)
                for f in post_parsed_content["files"]:
                    sql_query = "INSERT INTO resources (entry_uuid, path) VALUES (X'{}', '{}');".format(
                        id.hex, f
                    )
                    mysql_cursor.execute(sql_query)
                mysql_conn.commit()
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "http://localhost:4200")
                self.end_headers()
                self.wfile.write(base64.urlsafe_b64encode(id.bytes))

            else:
                self.send_response(401)
                self.send_header("Access-Control-Allow-Origin", "http://localhost:4200")
                self.end_headers()
        elif parsed_path.path.startswith("/upload/"):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "http://localhost:4200")
            self.end_headers()
            content_len = int(self.headers.get("Content-Length"))
            post_content = self.rfile.read(content_len)
            with open("test.jpg","wb") as f:
                f.write(post_content)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "http://localhost:4200")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-api-key,Content-Type")
        self.end_headers()


def run(server_class=HTTPServer, handler_class=RequestHandler, port=5764):
    logging.basicConfig(level=logging.INFO)
    server_address = ("localhost", port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")


run()

# close mysql connection
mysql_cursor.close()
mysql_conn.disconnect()
