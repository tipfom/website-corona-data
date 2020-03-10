import logging
import os
from http.server import HTTPServer

import mysql.connector

from config import *
from requesthandler import HTTPRequestHandler

if not os.path.exists(res_folder):
    os.mkdir(res_folder)

# Verbindung mit der Datenbank
mysql_conn = mysql.connector.connect(
    host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pass
)
mysql_conn.database = mysql_db
mysql_cursor = mysql_conn.cursor()


def run(
    server_class=HTTPServer, handler_class=HTTPRequestHandler(mysql_cursor), port=5764
):
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
