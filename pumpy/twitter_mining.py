# coding: utf-8

import csv
import json
import re
from typing import Any, List, Union, Tuple

import tweepy
from loguru import logger
from pathlib import Path
from tweepy import API, OAuthHandler, Status, Stream, StreamListener

from urllib3.exceptions import ReadTimeoutError

from .authapi import AuthApi
from .listener import ListenerBot, ListenerConsole, ListenerDB

LOGGER_ROOT = "./logs/"
logger.add(LOGGER_ROOT + "general.log", level="DEBUG", rotation="5 MB")

# TODO Use "extended" mode https://github.com/tweepy/tweepy/issues/974


class MinerStream(object):
    """Class used to Stream tweets and send them to a location (DB, file, console, bot...)
    
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

        elif self._output == "bot":
            logger.info("Start running a bot to send message to specific users")
            counter = 0
            logger.info("Run loop n°{counter}", counter=counter)
            api: API = tweepy.API(current_auth_handler[0])
            stream = Stream(self.current_auth_handler[0], ListenerBot(api))
            try:
                self._filter(stream)
            except tweepy.error.RateLimitError:
                logger.info("Rate limit reached, changing account")
                self._auth_next_account()
                counter += 1
            except ReadTimeoutError:
                logger.info("Raised a ReadTimeoutError :: Restart the service")
                self.mine()

        elif self._output == "database":
            try:
                self._streamer_db(self.config, self.current_auth_handler)
            except ReadTimeoutError:
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
    def _streamer_bot(self, auth_handler):
        pass

    @logger.catch()
    def _streamer_db(self, config, auth_handler):
        logger.debug("Generating the API")
        api: API = tweepy.API(auth_handler)
        stream = Stream(auth_handler, ListenerDB(api, config))
        self._filter(stream)

    @logger.catch()
    def _streamer_console(self, auth_handler):
        logger.debug("Generating the API")
        api: API = tweepy.API(auth_handler)
        stream = Stream(self.current_auth_handler[0], ListenerConsole(api))
        self._filter(stream)

    def _filter(self, stream: Stream):
        if self.keywords:
            stream.filter(track=self.keywords, is_async=True)
        elif self.locations:
            stream.filter(locations=self.locations, is_async=True)
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


class MinerFromPast(object):
    @logger.catch()
    def __init__(self):
        logger.info("Creating miner")
        # Auth management
        self.auth_keys: List[AuthApi] = list()
        self.current_auth_idx = 0
        self.current_auth_handler = None

        # Attributes when using a file as a source.
        self.input_file_path: Path = None
        self.output_file_path: str = str()
        self.index_ids: int = 0

    @logger.catch()
    def from_file(self, path_input_file: str, index_ids: int):
        """
        In 'getter' mode, define where are located the data that the user user wants
        to retrieve.
        
        Returns:
            Miner -- the current object.
        """
        logger.info("Entering from_file definition")
        logger.info(f"Mining data from a file located at {path_input_file}")
        logger.info(f"Text column is located at index {index_ids}")
        try:
            path: Path = Path(path_input_file)
        except FileNotFoundError:
            logger.error("Wrong file or file path")
        self.input_file_path = path
        self.index_ids = index_ids
        return self

    @logger.catch()
    def to(self, output):
        """Define where the data will be sent. It can be stdout, in a file or in a database
        
        Arguments:
            output {str} -- Path toward the directory where the data will be stored.
        
        Returns:
            Path -- Path object toward the file where the data will be stored.
        """
        logger.info("Entering output definition")
        if self.input_file_path is None:
            logger.error("No input file provided when calling .to()")

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
        logger.info("Entering Miner")
        logger.info("Accessing an auth key in the auth_keys list")
        auth_key: AuthApi = self.auth_keys[self.current_auth_idx]
        if auth_key.mode != self.mode:
            logger.error("The key mode mismatch the miner mode")
        else:
            logger.info("Generating the API")
            self.current_auth_handler: Tuple[OAuthHandler, str] = auth_key._generate_api

        if self.mode == "getter":
            self._file_ids_to_tweets_in_json(
                self, self.current_auth_handler, self.input_file_path
            )

        elif self.mode == "stream":
            if self._output == "console":
                logger.debug(f"The output mode is set to '{self._output}'")
                logger.debug(self.current_auth_handler)
                stream = Stream(
                    self.current_auth_handler[0], self._listener(self._output)
                )
                stream.filter(
                    track=self.keywords, locations=self.locations, is_async=True
                )
                logger.info("Starting collecting tweets")

            elif self._output == "database":
                logger.info("Start mining in 'stream' mode into the database")
                stream = Stream(
                    self.current_auth_handler[0],
                    self._listener(self._output, config=self.config),
                )
                stream.filter(
                    track=self.keywords, locations=self.locations, is_async=True
                )

        else:
            logger.error("The 'mode' argument provided to the miner is invalid.")
            logger.error("It should be 'getter' or 'stream")

    def db_config(
        self, host="localhost", port=27017, db="twitter", collection="tweet"
    ) -> None:
        logger.info("Entering db configuration")
        config = {"host": host, "port": port, "db": db, "collection": collection}
        logger.info("Database configuration set to {config}", config=config)
        self.config = config

    @staticmethod
    @logger.catch()
    def _write_tweets_through_ids(
        api: API, list_ids: List[str], path_tweet_json: Path
    ) -> None:
        tweets: List[str] = list()
        with open(str(path_tweet_json), "a+", encoding="utf-8") as resulting_json:
            for tweet_id in list_ids:
                try:
                    tweet = api[0].get_status(tweet_id)._json
                except tweepy.error.TweepError as err:
                    logger.warning(f"{tweet_id} | {err}")
                else:
                    tweets.append(tweet)

            json.dump(tweets, resulting_json, ensure_ascii=False, indent=4)
            # TODO Add information about the tweet acquisition (% of tweets retrieved)

    @staticmethod
    @logger.catch()
    def _file_ids_to_tweets_in_json(self, api: API, path_tweet_ids_csv: Path) -> None:
        # TODO: yield directement les ids au lieu de créer une liste
        ids: List[str] = list()
        with open(path_tweet_ids_csv, "r", encoding="utf-8") as ids_csv:
            csv_reader = csv.reader(ids_csv)
            for line in csv_reader:
                ids.append(line[self.index_ids])

        self._write_tweets_through_ids(api, ids, self.output_file_path)

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
