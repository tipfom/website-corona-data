import base64
import json
import logging
import uuid
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from random import randint, randrange
from urllib.parse import urlparse, parse_qs

import mysql.connector

from config import *

PROTOCOL_VERSION = "0.1"

ALLOWED_TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
valid_tokens = []

if not os.path.exists(res_folder):
    os.mkdir(res_folder)

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
        is_public = self.headers.__contains__("PROXY")
        splitted = parsed_path.path.split("/")
        if splitted[1] == "file":
            with open(res_folder + splitted[2] + ".json") as f:
                infofile_parsed = json.loads(f.read())
                extension = infofile_parsed["extension"]
                filetype = infofile_parsed["filetype"]
                filename = infofile_parsed["filename"]

                self.send_response(200)
                self.send_header("Content-Type", filetype)
                self.send_header(
                    "Content-Disposition",
                    'inline; filename="' + filename + "." + extension,
                )
                self.send_header("Access-Control-Allow-Origin", "http://localhost:4200")
                self.end_headers()
                with open(res_folder + splitted[2] + "." + extension, "rb") as f:
                    self.wfile.write(f.read())
        elif not is_public:
            if splitted[1] == "resource":
                if len(splitted) == 3:
                    try:
                        id = base64.urlsafe_b64decode(splitted[2] + "==").hex()
                    except Exception:
                        self.send_response(400)
                        self.end_headers()
                        return

                    sql_query = "SELECT type FROM entries WHERE uuid=X'{}'".format(id)
                    mysql_cursor.execute(sql_query)
                    row = mysql_cursor.fetchone()
                    if row != None:
                        self.send_response(200)
                        self.send_header(
                            "Access-Control-Allow-Origin", "http://localhost:4200"
                        )
                        self.end_headers()
                        self.wfile.write((row[0]).encode())
                        sql_query = "SELECT path FROM resources WHERE entry_uuid=X'{}'".format(
                            id
                        )
                        mysql_cursor.execute(sql_query)
                        for row in mysql_cursor.fetchall():
                            self.wfile.write(("\n" + row[0]).encode())
                    else:
                        self.send_response(404)
                        self.end_headers()
                else:
                    self.send_response(400)
                    self.end_headers()
        else:
            self.send_response(401)
            self.end_headers()


    def do_POST(self):
        if self.headers.__contains__("PROXY"):
            self.send_response(401)
            self.end_headers()
            return

        parsed_path = urlparse(self.path)
        parsed_query = parse_qs(parsed_path.query)
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
                for blobfile in post_parsed_content["files"]:
                    sql_query = "INSERT INTO resources (entry_uuid, path) VALUES (X'{}', '{}');".format(
                        id.hex, blobfile
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
            filename = str(uuid.uuid4().hex)
            with open(
                res_folder + filename + "." + parsed_query["e"][0], "wb+"
            ) as blobfile:
                blobfile.write(post_content)
            with open(res_folder + filename + ".json", "w+") as infofile:
                json.dump(
                    {
                        "extension": parsed_query["e"][0],
                        "filetype": parsed_query["t"][0],
                        "filename": parsed_query["n"][0],
                    },
                    infofile,
                )

            self.wfile.write(filename.encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "http://localhost:4200")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-api-key,Content-Type")
        self.end_headers()


def run(server_class=HTTPServer, handler_class=RequestHandler, port=5764):
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

# close mysql connection
mysql_cursor.close()
mysql_conn.disconnect()
