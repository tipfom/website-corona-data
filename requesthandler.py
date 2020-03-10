import base64
import json
import os
import uuid
from http.server import BaseHTTPRequestHandler
from random import randint, randrange
from urllib.parse import parse_qs, urlparse

from config import *
from mysqlconnection import MySqlConnection

ALLOWED_TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
valid_tokens = []


if not os.path.exists(res_folder):
    os.mkdir(res_folder)


def generateToken(length):
    token = ""
    for _ in range(length):
        token += ALLOWED_TOKEN_CHARS[randrange(len(ALLOWED_TOKEN_CHARS))]
    return token


globalSqlConnection = MySqlConnection(
    mysql_db, mysql_host, mysql_pass, mysql_port, mysql_user
)


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.sqlConnection = globalSqlConnection
        super().__init__(request, client_address, server)

    def do_GET(self):
        parsed_path = urlparse(self.path)
        is_authorized = self.headers.__contains__("LOGIN-TOKEN") and valid_tokens.__contains__(self.headers.get("LOGIN-TOKEN"))
        splitted = parsed_path.path.split("/")
        if splitted[1] == "file":
            try:
                with open(res_folder + splitted[2] + ".json") as f:
                    infofile_parsed = json.loads(f.read())
                    extension = infofile_parsed["extension"]
                    filetype = infofile_parsed["filetype"]
                    filename = infofile_parsed["filename"]

                    with open(res_folder + splitted[2] + "." + extension, "rb") as f:
                        self.send_response(200)
                        self.send_header("Content-Type", filetype)
                        self.send_header(
                            "Content-Disposition", 'inline; filename="' + filename,
                        )

                        self.send_header(
                            "Content-Length",
                            str(
                                os.stat(
                                    res_folder + splitted[2] + "." + extension
                                ).st_size
                            ),
                        )
                        self.send_header(
                            "Access-Control-Allow-Origin", "*"
                        )
                        self.end_headers()

                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            self.wfile.write(data)
            except Exception as e:
                print(e)
                self.send_response(404)
                self.end_headers()

        elif not is_authorized:
            if splitted[1] == "resource":
                if len(splitted) == 3:
                    try:
                        id = base64.urlsafe_b64decode(splitted[2] + "==").hex()
                    except Exception:
                        self.send_response(400)
                        self.end_headers()
                        return

                    sql_query = "SELECT type FROM entries WHERE uuid=X'{}'".format(id)
                    self.sqlConnection.execute(sql_query)
                    row = self.sqlConnection.fetchone()
                    if row != None:
                        self.send_response(200)
                        self.send_header(
                            "Access-Control-Allow-Origin", "*"
                        )
                        self.end_headers()
                        self.wfile.write((row[0]).encode())
                        sql_query = "SELECT path FROM resources WHERE entry_uuid=X'{}'".format(
                            id
                        )
                        self.sqlConnection.execute(sql_query)
                        for row in self.sqlConnection.fetchall():
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
        is_authorized = self.headers.__contains__("LOGIN-TOKEN") and valid_tokens.__contains__(self.headers.get("LOGIN-TOKEN"))

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
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(('{"token":"' + new_token + '"}').encode())
            else:
                self.send_response(401)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
        elif is_authorized:
            if parsed_path.path.startswith("/resource"):
                content_len = int(self.headers.get("Content-Length"))
                post_content = self.rfile.read(content_len)
                post_parsed_content = json.loads(post_content)
                
                id = uuid.uuid4()
                content_type = post_parsed_content.get("type")
                sql_query = f"INSERT INTO entries (uuid, type) VALUES (X'{id.hex}', '{content_type}');"
                self.sqlConnection.execute(sql_query)
                for blobfile in post_parsed_content["files"]:
                    sql_query = f"INSERT INTO resources (entry_uuid, path) VALUES (X'{id.hex}', '{blobfile}');"
                    self.sqlConnection.execute(sql_query)
                self.sqlConnection.commit()
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(base64.urlsafe_b64encode(id.bytes))

            elif parsed_path.path.startswith("/upload/"):
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
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
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(401)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "LOGIN-TOKEN,Content-Type")
        self.end_headers()
