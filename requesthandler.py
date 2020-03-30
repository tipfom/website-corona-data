import base64
import json
import os
import uuid
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from config import *
from mysqlconnection import MySqlConnection
from sessionmanager import SessionManager
from passwords import *
from corona.data import datasets_json, topcountries_json, serious_dataset, serious_last_refreshed

if not os.path.exists(res_folder):
    os.mkdir(res_folder)

globalSqlConnection = MySqlConnection(
    mysql_db, mysql_host, mysql_password, mysql_port, mysql_user
)

globalSessionManager = SessionManager()

article_cache = {}


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
        parsed_query = parse_qs(parsed_path.query)
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
        elif splitted[1] == "corona":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(datasets_json[splitted[2]])
        elif splitted[1] == "coronatop":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(topcountries_json)
        elif splitted[1] == "coronaserious":
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if serious_dataset.__contains__(splitted[2]):
                self.wfile.write((serious_last_refreshed + "\n" + serious_dataset[splitted[2]]).encode())
            else:
                self.wfile.write((serious_last_refreshed + "\n" +"not-available").encode())
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
                sql_query = "SELECT name, creation_time, title_de, description_de, title_en, description_en FROM articles"
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
                            "title_de": row[2],
                            "description_de": row[3],
                            "title_en": row[4],
                            "description_en": row[5],
                        }
                    )
                self.wfile.write(json.dumps(articles).encode())
            elif splitted[2] == "detail":
                sql_query = "SELECT article_id, title_de, description_de, title_en, description_en, creation_time FROM articles WHERE name=%s"
                self.sqlConnection.execute(sql_query, (splitted[3],))
                article = self.sqlConnection.fetchone()
                if article:
                    article_id = article[0]
                    sql_query = "SELECT version_id, creation_time FROM article_versions WHERE article_id=%s ORDER BY version_id"
                    self.sqlConnection.execute(sql_query, (article_id,))
                    versions = []
                    for version_row in self.sqlConnection.fetchall():
                        versions.append(
                            {
                                "id": version_row[0],
                                "creation_time": version_row[1],
                                "files": [],
                            }
                        )

                    files = []
                    for version in versions:
                        sql_query = "SELECT lang, path FROM article_version_files WHERE version_id=%s"
                        self.sqlConnection.execute(sql_query, (version["id"],))
                        version_files = []
                        for file_row in self.sqlConnection.fetchall():
                            version_files.append(
                                {
                                    "lang": file_row[0],
                                    "path": file_row[1],
                                    "creation_time": version["creation_time"].isoformat(),
                                }
                            )
                        files.append(version_files)

                    self.send_response(200)
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(
                        json.dumps(
                            {
                                "title_de": article[1],
                                "description_de": article[2],
                                "title_en": article[3],
                                "description_en": article[4],
                                "creation_time": article[5].isoformat(),
                                "files": files,
                            }
                        ).encode()
                    )
                else:
                    self.send_response(404)
                    self.end_headers()
            elif splitted[2] == "content":
                try:
                    if not article_cache.__contains__(splitted[3]):
                        with open(articles_folder + splitted[3], "rb") as f:
                            article_cache.update({splitted[3]: f.read()})
                    self.send_response(200)
                    self.send_header("Content-Type", "text/markdown; charset=UTF-8")
                    self.send_header(
                        "Content-Length",
                        str(os.stat(articles_folder + splitted[3]).st_size),
                    )
                    self.send_header("Content-Disposition", "inline")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(article_cache[splitted[3]])

                except Exception:
                    self.send_response(404)
                    self.end_headers()
            elif splitted[2] == "spotlight":
                sql_query = "SELECT name, title_de, description_de, title_en, description_en FROM articles WHERE is_spotlight = 1 ORDER BY name"
                self.sqlConnection.execute(sql_query)
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                articles = []
                for row in self.sqlConnection.fetchall():
                    articles.append(
                        {
                            "name": row[0],
                            "title_de": row[1],
                            "description_de": row[2],
                            "title_en": row[3],
                            "description_en": row[4],
                        }
                    )
                self.wfile.write(json.dumps(articles).encode())

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
                if post_parsed_content["password"] == admin_password:
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

                sql_query = "SELECT article_id FROM articles WHERE name=%s"
                self.sqlConnection.execute(sql_query, (parsed_query["name"][0],))
                article_id = self.sqlConnection.fetchone()
                if not article_id:
                    sql_query = "INSERT INTO articles (name, title_de, description_de, title_en, description_en) VALUES (%s, %s, %s, %s, %s)"
                    self.sqlConnection.execute(
                        sql_query,
                        (
                            parsed_query["name"][0],
                            parsed_query["title_de"][0],
                            parsed_query["description_de"][0],
                            parsed_query["title_en"][0],
                            parsed_query["description_en"][0],
                        ),
                    )
                    self.sqlConnection.commit()
                    sql_query = "SELECT article_id FROM articles WHERE name=%s"
                    self.sqlConnection.execute(sql_query, (parsed_query["name"][0],))
                    article_id = self.sqlConnection.fetchone()

                version_id = ""
                if parsed_query.__contains__("version_id"):
                    version_id = parsed_query["version_id"][0]
                else:
                    sql_query = "INSERT INTO article_versions (article_id) VALUES (%s);"
                    self.sqlConnection.execute(sql_query, (article_id[0],))
                    self.sqlConnection.commit()
                    sql_query = "SELECT MAX(version_id) FROM article_versions"
                    self.sqlConnection.execute(sql_query)
                    version_id = self.sqlConnection.fetchone()[0]

                sql_query = "INSERT INTO article_version_files (version_id, lang, path) VALUES (%s, %s, %s)"
                self.sqlConnection.execute(
                    sql_query, (version_id, parsed_query["lang"][0], filename)
                )
                self.sqlConnection.commit()
                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(str(version_id).encode())
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
