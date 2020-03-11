from datetime import datetime, timedelta
from random import randrange
from threading import Lock
import hashlib

ALLOWED_TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

lock = Lock()


class SessionManager:
    def __init__(self):
        self._active_tokens = {}

    def isActiveSession(self, ip, token):
        if ip == None:
            return False
            
        lock.acquire()
        if self._active_tokens.__contains__((ip, token)):
            if datetime.now() < self._active_tokens[(ip, token)]:
                lock.release()
                return True
            else:
                self._active_tokens.pop((ip, token))
        lock.release()
        return False

    def createSession(self, ip, token_length, validity_time=timedelta(days=1)):
        token = ""
        for _ in range(token_length):
            token += ALLOWED_TOKEN_CHARS[randrange(len(ALLOWED_TOKEN_CHARS))]
        expiration_time = datetime.now() + validity_time

        self._active_tokens.update({(ip, token): expiration_time})
        return token
