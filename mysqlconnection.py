import mysql.connector

from config import mysql_db, mysql_host, mysql_pass, mysql_port, mysql_user

# Verbindung mit der Datenbank
mysql_conn = None
mysql_cursor = None


def getMySQLCursor():
    return mysql_cursor


def openMySQLConnection():
    global mysql_conn
    global mysql_cursor
    mysql_conn = mysql.connector.connect(
        host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_pass
    )
    mysql_conn.database = mysql_db
    mysql_cursor = mysql_conn.cursor()
    return mysql_conn


def closeMySQLConnection():
    global mysql_conn
    global mysql_cursor
    if mysql_conn == None:
        return
    # close mysql connection
    mysql_cursor.close()
    mysql_conn.disconnect()
