import logging

import mysql.connector

# Verbindung mit der Datenbank
class MySqlConnection():
    def __init__(self, mysql_db, mysql_host, mysql_pass, mysql_port, mysql_user):
        self.mysql_conn = mysql.connector.connect(
            host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pass
        )
        self.mysql_conn.database = mysql_db
        self.mysql_cursor = self.mysql_conn.cursor()
        logging.info("MySqlConnection created\n")

    def __del__(self):
        if self.mysql_conn == None:
            return
        # close mysql connection
        self.mysql_cursor.close()
        self.mysql_conn.disconnect()
