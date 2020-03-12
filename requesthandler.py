import base64
import json
import os
import uuid
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from config import *
from mysqlconnection import MySqlConnection
from sessionmanager import SessionManager

if not os.path.exists(res_folder):
    os.mkdir(res_folder)

globalSqlConnection = MySqlConnection(
    mysql_db, mysql_host, mysql_pass, mysql_port, mysql_user
)

globalSessionManager = SessionManager()


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.sqlConnection = globalSqlConnection
        super().__init__(request, client_address, server)

    def get_client_ip(self):
        if self.headers.__contains__("PROXY"):
            if self.headers.__contains__("X-FORWARDED-FOR"):
                return self.headers.get("X-FORWARDED-FOR")
        else:
            return self.client_address[0]
        return None

    def do_GET(self):
        parsed_path = urlparse(self.path)
        is_authorized = self.headers.__contains__(
            "LOGIN-TOKEN"
        ) and globalSessionManager.isActiveSession(
            self.get_client_ip(), self.headers.get("LOGIN-TOKEN")
        )
        splitted = parsed_path.path.split("/")
        if len(splitted) < 2:
            self.send_response(400)
            self.end_headers()
            return

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
                        self.send_header("Access-Control-Allow-Origin", "*")
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
        elif splitted[1] == "authorized":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(str(is_authorized).encode())
        elif splitted[1] == "resource":
            if len(splitted) == 3:
                try:
                    id = base64.urlsafe_b64decode(splitted[2] + "==").hex()
                except Exception:
                    self.send_response(400)
                    self.end_headers()
                    return

                sql_query = f"SELECT type, creation_time, path FROM resources WHERE entry_uuid=X'{id}';"
                self.sqlConnection.execute(sql_query)
                row = self.sqlConnection.fetchone()
                if row != None:
                    self.send_response(200)
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    queried_resources = []
                    while row:
                        queried_resources.append(
                            {
                                "type": row[0],
                                "creation_time": row[1].isoformat(),
                                "path": row[2],
                            }
                        )
                        row = self.sqlConnection.fetchone()
                    self.wfile.write(json.dumps(queried_resources).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            else:
                self.send_response(400)
                self.end_headers()
        elif splitted[1] == "articles":
            if splitted[2] == "all":
                sql_query = "SELECT a1.name, a1.creation_time, a1.file FROM articles a1 WHERE a1.creation_time = (SELECT MAX(creation_time) FROM articles a2 WHERE a1.name = a2.name);"
                self.sqlConnection.execute(sql_query)
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                articles = []
                for row in self.sqlConnection.fetchall():
                    articles.append(
                        {
                            "name": row[0],
                            "creation_time": row[1].isoformat(),
                            "file": row[2],
                        }
                    )
                self.wfile.write(json.dumps(articles).encode())
            elif splitted[2] == "versions":
                sql_query = (
                    "SELECT name, creation_time, file FROM articles WHERE name=%s ORDER BY creation_time"
                )
                self.sqlConnection.execute(sql_query, (splitted[3],))
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                articles = []
                for row in self.sqlConnection.fetchall():
                    articles.append(
                        {
                            "name": row[0],
                            "creation_time": row[1].isoformat(),
                            "file": row[2],
                        }
                    )
                self.wfile.write(json.dumps(articles).encode())
            elif splitted[2] == "content":
                try:
                    with open(articles_folder + splitted[3], "rb") as f:
                        self.send_response(200)
                        self.send_header("Content-Type", "text/markdown; charset=UTF-8")
                        self.send_header(
                            "Content-Length",
                            str(os.stat(articles_folder + splitted[3]).st_size),
                        )
                        self.send_header(
                            "Content-Disposition", "inline"
                        )
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            self.wfile.write(data)

                except Exception:
                    self.send_response(404)
                    self.end_headers()

        else:
            self.send_response(401)
            self.end_headers()

    def do_POST(self):
        is_authorized = self.headers.__contains__(
            "LOGIN-TOKEN"
        ) and globalSessionManager.isActiveSession(
            self.get_client_ip(), self.headers.get("LOGIN-TOKEN")
        )

        parsed_path = urlparse(self.path)
        parsed_query = parse_qs(parsed_path.query)
        if parsed_path.path.startswith("/login"):
            try:
                content_len = int(self.headers.get("Content-Length"))
                post_content = self.rfile.read(content_len)
                post_parsed_content = json.loads(post_content)
                if post_parsed_content["password"] == "ME^WDKn$mL6c74eq":
                    self.send_response(201)
                    new_token = globalSessionManager.createSession(
                        self.get_client_ip(), 32
                    )
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(('{"token":"' + new_token + '"}').encode())
                else:
                    self.send_response(401)
                    self.end_headers()
            except Exception:
                self.send_response(400)
                self.end_headers()

        elif is_authorized:
            if parsed_path.path.startswith("/resource"):
                content_len = int(self.headers.get("Content-Length"))
                post_content = self.rfile.read(content_len)
                post_parsed_content = json.loads(post_content)

                id = uuid.uuid4()
                content_type = post_parsed_content.get(
                    "type"
                )  # TODO: CHECK CONTENT TYPE
                for blobfile in post_parsed_content["files"]:
                    sql_query = "INSERT INTO resources (type, path, entry_uuid) VALUES (%s, %s, X%s);"
                    self.sqlConnection.execute(
                        sql_query, (content_type, blobfile, id.hex)
                    )
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
            elif parsed_path.path.startswith("/article"):
                content_len = int(self.headers.get("Content-Length"))
                post_content = self.rfile.read(content_len)
                filename = str(uuid.uuid4().hex) + ".md"
                with open(articles_folder + filename, "wb+") as blobfile:
                    blobfile.write(post_content)
                sql_query = "INSERT INTO articles (name, file) VALUES (%s, %s)"
                self.sqlConnection.execute(
                    sql_query, (parsed_query["name"][0], filename)
                )
                self.sqlConnection.commit()

                self.send_response(200)
                self.end_headers()
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
