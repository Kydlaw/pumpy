from pymongo import MongoClient


class MongoDB(object):
    def __init__(self):
        self.localhost = "localhost"
        self.port = 27017
        self.db_name = "test_database"
        self.collection_name = "test_collection"

    @property
    def init(self):
        client = MongoClient(self.localhost, self.port)
        db = client[self.db_name]
        collection = db[self.collection_name]
        return db
