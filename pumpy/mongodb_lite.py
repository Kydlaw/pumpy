from pymongo import MongoClient


class MongoDB(object):
    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        db_name: str = "test_database",
        collection_name: str = "test_collection",
    ):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.collection_name = collection_name

    @property
    def init(self) -> MongoClient:
        client = MongoClient(self.host, self.port)
        db = client[self.db_name]
        collection = db[self.collection_name]
        return db
