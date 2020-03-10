from datetime import datetime, timedelta
from random import randrange
from threading import Lock

ALLOWED_TOKEN_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"

lock = Lock()

class SessionManager:
    def __init__(self):
        self._active_tokens = {}

    def isActiveSession(self, token):
        lock.acquire()
        if self._active_tokens.__contains__(token):
            if datetime.now() < self._active_tokens[token]:
                lock.release()
                return True
            else:
                self._active_tokens.pop(token)
        lock.release()
        return False

    def createSession(self, token_length):
        token = ""
        for _ in range(token_length):
            token += ALLOWED_TOKEN_CHARS[randrange(len(ALLOWED_TOKEN_CHARS))]
        self._active_tokens.update({token: datetime.now() + timedelta(days=1)})
        return token
