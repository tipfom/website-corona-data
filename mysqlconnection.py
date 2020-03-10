import logging

import mysql.connector

logging.getLogger().setLevel(logging.INFO)

# Verbindung mit der Datenbank
class MySqlConnection:
    def __init__(self, mysql_db, mysql_host, mysql_pass, mysql_port, mysql_user):
        self.mysql_db = mysql_db
        self.mysql_host = mysql_host
        self.mysql_pass = mysql_pass
        self.mysql_port = mysql_port
        self.mysql_user = mysql_user

        self._mysql_conn = mysql.connector.connect(
            host=self.mysql_host,
            port=self.mysql_port,
            user=self.mysql_user,
            password=self.mysql_pass,
        )
        self._mysql_conn.database = self.mysql_db
        self._mysql_cursor = self._mysql_conn.cursor()

        logging.info("MySqlConnection initialized")

    def __del__(self):
        if self._mysql_conn == None:
            return
        # close mysql connection
        self._mysql_cursor.close()
        self._mysql_conn.disconnect()

    def checkConnection(self):
        if not self._mysql_conn.is_connected():
            self._mysql_conn.reconnect()
            self._mysql_conn.database = self.mysql_db
            self._mysql_cursor = self._mysql_conn.cursor()

        if not self._mysql_conn.is_connected():
            logging.error("could not connect to database")

    def execute(self, cmd, params=()):
        self.checkConnection()
        return self._mysql_cursor.execute(cmd, params)

    def fetchone(self):
        self.checkConnection()
        return self._mysql_cursor.fetchone()

    def fetchall(self):
        self.checkConnection()
        return self._mysql_cursor.fetchall()

    def commit(self):
        self.checkConnection()
        return self._mysql_conn.commit()

