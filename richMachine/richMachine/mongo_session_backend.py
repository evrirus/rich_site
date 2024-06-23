import datetime
from pymongo import MongoClient
from django.conf import settings
from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.contrib.sessions.exceptions import InvalidSessionKey
from django.utils.crypto import get_random_string

class MongoSession(SessionBase):
    def __init__(self, session_key=None):
        super().__init__(session_key)
        self.client = MongoClient(settings.MONGO_SESSION_URI)
        self.collection = self.client[settings.MONGO_SESSION_DB][settings.MONGO_SESSION_COLLECTION]

    def _get_new_session_key(self):
        while True:
            session_key = get_random_string(32)
            if not self.exists(session_key):
                return session_key

    def exists(self, session_key):
        return self.collection.count_documents({"_id": session_key}) > 0

    def load(self):
        session_data = self.collection.find_one({"_id": self.session_key})
        if session_data:
            return self.decode(session_data["session_data"])
        self.create()
        return {}

    def create(self):
        while True:
            self.session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            self._session_cache = {}
            break

    def save(self, must_create=False):
        session_data = {
            "_id": self.session_key,
            "session_data": self.encode(self._session),
            "expire_date": self.get_expiry_date(),
        }
        if must_create and self.exists(self.session_key):
            raise CreateError
        self.collection.update_one(
            {"_id": self.session_key},
            {"$set": session_data},
            upsert=True
        )

    def delete(self, session_key=None):
        if session_key is None:
            session_key = self.session_key
        self.collection.delete_one({"_id": session_key})

    def get_expiry_date(self):
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=self.get_expiry_age())
