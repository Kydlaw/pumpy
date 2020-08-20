# coding: utf-8

from http.client import IncompleteRead
from typing import List, Tuple

import tweepy
from loguru import logger
from tweepy import API, OAuthHandler, Stream
from urllib3.exceptions import ProtocolError, ReadTimeoutError

from .authapi import AuthApi
from .listener import ListenerConsole, ListenerDB

LOGGER_ROOT = "./logs/"
logger.add(LOGGER_ROOT + "general.log", level="DEBUG", rotation="5 MB")

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

    @logger.catch()
    def __init__(self):
        # Attributes related to Auth management
        self.auth_keys: List[AuthApi] = list()
        self.current_auth_idx: int = 0
        self.current_auth_handler: OAuthHandler = None

        #  Attributes related to the Stream API
        self.keywords: List[str] = list()
        self.locations: List[List[int]] = list()

    @logger.catch()
    def to(self, output):
        """
        Define where the data will be sent. It can be stdout, file file, database or
        sent to a bot.
        
        Arguments:
            output {str} -- Where the data will be directed.
        """
        if output == "database":
            logger.info("Output mode set to database")
            self._output = output
            return self
        elif output == "console":
            logger.info("Output mode set to console")
            self._output = output
        elif output == "bot":
            logger.info("Output mode set to bot")
            self._output = output
        else:
            logger.error("Invalid output mode passed")

    @logger.catch()
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
                logger.error("Raised a ReadTimeoutError :: Restart the service")
                self.mine()
            except ProtocolError:
                logger.error("Raised a ProtocolError :: Restart the service")
                self.mine()
            except IncompleteRead:
                logger.error("Raised an IncompleteRead error :: Restart the service")
                self.mine()

    def search(self, *args) -> None:
        """
        Define the keywords or locations sent to the Twitter API to get the tweets.
        """
        logger.info("Search arguments definition")
        for elt in args:
            if type(elt) == str:
                self.keywords.append(elt)
            elif type(elt) == list and len(elt) == 4:
                self.locations.append(elt)
            else:
                logger.error("Invalid keywords or locations provided to .search()")
        logger.debug(f"Keywords use to search :: {self.keywords}")

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
        logger.info("DB configuration")
        config = {"host": host, "port": port, "db": db, "collection": collection}
        logger.debug("Database configuration set to: {config}", config=config)
        self.config = config

    @logger.catch()
    def _streamer_db(self, config, auth_handler):
        logger.debug("Generating the API")
        api: API = tweepy.API(auth_handler)
        stream = Stream(auth_handler, ListenerDB(api, config))
        try:
            self._filter(stream)
        except IncompleteRead:
            logger.error("Raised an IncompleteRead error :: Restart the service")
            self.mine()

    @logger.catch()
    def _streamer_console(self, auth_handler):
        logger.debug("Generating the API")
        api: API = tweepy.API(auth_handler)
        stream = Stream(self.current_auth_handler[0], ListenerConsole(api))
        self._filter(stream)

    def _filter(self, stream: Stream):
        if self.keywords:
            stream.filter(track=self.keywords, async=True)
        elif self.locations:
            stream.filter(locations=self.locations, async=True)
        else:
            logger.debug("Failed to start stream.")
        logger.info("...Stream started...")

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
