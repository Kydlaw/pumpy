# coding: utf-8

import queue
from threading import Thread

from pymongo import MongoClient
from pymongo.database import Database, Collection
from tweepy import StreamListener


class ListenerConsole(StreamListener):
    def __init__(self, api, sample=15, test=False):
        StreamListener.__init__(self, api)
        self.index_RT: int = 1
        self.sample: int = sample
        self.test: bool = test

    def on_status(self, status) -> None:
        if self.test:
            print(status.user.screen_name)
        else:
            if status.text[:2] == "RT" and self.index_RT % self.sample != 0:
                self.index_RT += 1
            elif status.text[:2] == "RT" and self.index_RT % self.sample == 0:
                status = status.id_str + " :: " + status.text.replace("\n", " \\n ")
                print(status)
                self.index_RT = 1
            else:
                status = status.id_str + " :: " + status.text.replace("\n", " \\n ")
                print(status)


class ListenerDB(StreamListener):
    """A StreamListener to store tweets in a DB. It has the following methods:
    - on_status() -- Action performed when a tweet matching the keyword is found
    - on_error() -- Method called to send a message to a specified user
    
    Properties:
        client {MongoClient} -- The MongoClient use to store tweets in the MongoDB
        db {Database} -- The MongoClient with the db's config passed to it.
        collection {Collection} -- The # of the current auth key used
        sample {int} -- The Twitter API object currently used by the bot
        index_RT {int} -- The message send by the bot to a user
    """

    def __init__(self, api, config, sample=15):
        StreamListener.__init__(self, api)
        self.client: MongoClient = MongoClient(config["host"], config["port"])
        self.db: Database = self.client[config["db"]]
        self.collection: Collection = self.db[config["collection"]]
        self.sample: int = sample
        self.index_RT: int = 1
        self.index_info: int = 0
        self.queue = queue.Queue()
        t = Thread(target=self._storing, daemon=True).start()

    def on_status(self, status):
        """Action to perform when a tweet containing a keyword(s) passed to the StreamListener
        is found.
        For the ListenerDB, it pushs tweets into the MongoDB. It samples every {sample} 
        retweets to avoid overflow.
        
        Arguments:
            status -- The tweet received
        """

        self.queue.put(status._json)
        self.index_info += 1

        if self.index_info == 100:
            print("Bip! :: Queue size = {qsize}", qsize=self.queue.qsize())
            self.index_info = 0

    def on_error(self, status_code):
        """Action to perform when an error occur.
        
        Arguments:
            status_code -- The code of the error captured
        """
        print(status_code)

    def on_timeout(self):
        self.client.close()

    def _storing(self):
        while True:
            status = self.queue.get()
            if status["text"][:2] == "RT" and self.index_RT % self.sample != 0:
                self.index_RT += 1
            elif status["text"][:2] == "RT" and self.index_RT % self.sample == 0:
                post_id = self.collection.insert_one(status)
                self.index_RT = 1
            else:
                post_id = self.collection.insert_one(status)
            self.queue.task_done()
