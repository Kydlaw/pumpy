# coding: utf-8

from http.client import IncompleteRead
from typing import List, Tuple

import tweepy
from tweepy import API, OAuthHandler, Stream
from urllib3.exceptions import ProtocolError, ReadTimeoutError

from .authapi import AuthApi
from .listener import ListenerConsole, ListenerDB


# TODO Use "extended" mode https://github.com/tweepy/tweepy/issues/974


class MinerStream(object):
    """Class used to receive Stream tweets and send them to a location (DB, console, bot)s
    
    Arguments:
        None
    
    Raises:
        ValueError: [description]
    
    Returns:
        Run a Tweepy Stream object
    """

    def __init__(self):
        # Attributes related to Auth management
        self.auth_keys: List[AuthApi] = list()
        self.current_auth_idx: int = 0
        self.current_auth_handler: OAuthHandler = None

        #  Attributes related to the Stream API
        self.keywords: List[str] = list()
        self.locations: Tuple[float] = ()

    def to(self, output):
        """
        Define where the data will be sent. It can be stdout, file file, database or
        sent to a bot.
        
        Arguments:
            output {str} -- Where the data will be directed.
        """
        if output == "database":
            self._output = output
            return self
        elif output == "console":
            self._output = output
        elif output == "bot":
            self._output = output
        else:
            raise ValueError("Invalid output mode passed")

    def mine(self):
        """
        Method to collect tweets.
        If a rate limit error is raised, switch the account used and restart the collection
        """
        if not (self.keywords or self.locations):
            raise ValueError("No keywords or location provided")

        auth_key: AuthApi = self.auth_keys[self.current_auth_idx]
        self.current_auth_handler = auth_key.generate_api
        api = self.current_auth_handler

        if self._output == "console":
            self._streamer_console(self.current_auth_handler)

        elif self._output == "database":
            try:
                self._streamer_db(self.config, self.current_auth_handler)
            except ReadTimeoutError:
                self.mine()
            except ProtocolError:
                self.mine()
            except IncompleteRead:
                self.mine()

    def search(self, *args) -> None:
        """
        Define the keywords or locations sent to the Twitter API to get the tweets.
        
        *Args:
            List[str]: Strings that are going to be asked to the API.
            _or_
            Tuple[float]: Tuple of 4 floats that will delimit the collection area.
        """
        for elt in args:
            if type(elt) == str:
                self.keywords.append(elt)
            elif type(elt) == tuple and len(elt) == 4:
                self.locations = elt

    def db_config(
        self, host="localhost", port=27017, db="twitter", collection="tweet"
    ) -> None:
        """
        Configuration of the Mongo database used to store the tweets retrieved.
        
        Keyword Arguments:
            host {str} -- Host's name (default: {"localhost"})
            port {int} -- Port used (default: {27017})
            db {str} -- The name of the database (default: {"twitter"})
            collection {str} -- The name of the collection used  (default: {"tweet"})
        """
        config = {"host": host, "port": port, "db": db, "collection": collection}
        self.config = config

    def _streamer_db(self, config, auth_handler):
        api: API = tweepy.API(auth_handler)
        stream = Stream(auth_handler, ListenerDB(api, config))
        try:
            self._filter(stream)
        except IncompleteRead:
            self.mine()
        except KeyboardInterrupt:
            stream.disconnect()

    def _streamer_console(self, auth_handler):
        api: API = tweepy.API(auth_handler)
        stream = Stream(self.current_auth_handler[0], ListenerConsole(api))
        self._filter(stream)

    def _filter(self, stream: Stream):
        if self.keywords:
            stream.filter(track=self.keywords, is_async=True)
        elif self.locations:
            stream.filter(locations=self.locations, is_async=True)

    def _auth_next_account(self):
        """
        Internal function that shouldn't be called outside of mine, it tries to
        grab the next account and if it reaches the end, it wraps back around to the
        first set of keys.

        :return: the new api, but it also sets self.api so unnecessary
        """
        self.current_auth_idx = self.current_auth_idx + 1
        if len(self.auth_keys) <= self.current_auth_idx:
            self.current_auth_idx = 0

        auth_key: AuthApi = self.auth_keys[self.current_auth_idx]
        self.current_auth_handler: Tuple[OAuthHandler, str] = auth_key._generate_api
