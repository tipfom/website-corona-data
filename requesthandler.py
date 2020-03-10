import base64
import json
import uuid
from http.server import BaseHTTPRequestHandler
from random import randint, randrange
from urllib.parse import parse_qs, urlparse

from config import res_folder

ALLOWED_TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
valid_tokens = []

def generateToken(length):
    token = ""
    for _ in range(length):
        token += ALLOWED_TOKEN_CHARS[randrange(len(ALLOWED_TOKEN_CHARS))]
    return token


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, mysql_cursor):
        self.mysql_cursor = mysql_cursor

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
                    self.mysql_cursor.execute(sql_query)
                    row = self.mysql_cursor.fetchone()
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
                        self.mysql_cursor.execute(sql_query)
                        for row in self.mysql_cursor.fetchall():
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
                self.mysql_cursor.execute(sql_query)
                for blobfile in post_parsed_content["files"]:
                    sql_query = "INSERT INTO resources (entry_uuid, path) VALUES (X'{}', '{}');".format(
                        id.hex, blobfile
                    )
                    self.mysql_cursor.execute(sql_query)
                self.mysql_cursor.commit()
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