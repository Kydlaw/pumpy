import csv
import json
import re
import typing
from typing import Any, List, Union

import tweepy
from loguru import logger
from path import Path
from pymongo import MongoClient
from tweepy import API, Status, Stream, StreamListener

from .creds import AuthApi
from .mongodb_lite import MongoDB

LOGGER_ROOT = "./logs/"

logger.add(LOGGER_ROOT + "general.log", level="DEBUG", rotation="5 MB")


class Miner(object):
    @logger.catch()
    def __init__(self, mode: str):
        logger.info(f"Creating miner in mode '{mode}'")
        if mode == "getter" or mode == "stream":
            self.mode: str = mode
        else:
            logger.error("The 'mode' used was not 'stream' nor 'getter'")
        self.input_file_path: Path = None
        self.output_file_path: str = str()
        self.index_ids: int = 0
        self.keywords: List[str] = list()
        self.locations: List[List[int]] = list()

    @logger.catch()
    def from_file(self, path_input_file: str, index_ids: int) -> "Miner":
        """In 'getter' mode, define where are located the data that the user user wants
        to retrieve.
        
        Returns:
            Miner -- the current object.
        """
        logger.info("Entering from_file definition")
        logger.info(f"Mining data from a file located at {path_input_file}")
        logger.info(f"Text column is located at index {index_ids}")
        if self.mode != "getter":
            logger.error("from_file() method is only available in 'getter' mode")
        try:
            path: Path = Path(path_input_file)
        except FileNotFoundError as err:
            logger.error("Wrong file or file path")
        self.input_file_path = path
        self.index_ids = index_ids
        return self

    @logger.catch()
    def to(self, output) -> Union[None, "Miner"]:
        """Define where the data will be sent. It can be stdout, in a file or in a database
        
        Arguments:
            output {str} -- Path toward the directory where the data will be stored.
        
        Returns:
            Path -- Path object toward the file where the data will be stored.
        """
        logger.info("Entering output definition")
        if self.input_file_path is None and self.mode == "getter":
            logger.error("No input file provided when calling .to()")

        if output == "database":
            logger.info("Output mode set to database")
            self._output = output
            return self
        elif output == "console":
            logger.info("Output mode set to console")
            self._output = output
        else:
            self._output = "file"
            logger.info("Output mode set to file")
            if self.mode == "getter":
                output_path = Path(output)
                self.output_file_path = self._new_file_name(
                    self, output_path, extension=".json"
                )
                logger.info(f"Sending data to {self.output_file_path}.")
            else:
                # TODO: Add test
                output_path = Path(output)
                file_index = 0
                while (output_path + f"stream{file_index}.txt").exists():
                    file_index += 1
                new_file_path = output_path + f"stream{file_index}.txt"
                self.output_file_path = new_file_path
                logger.info(f"Sending data to {new_file_path}.")

    @logger.catch()
    def mine(self, api: tuple):
        logger.info("Entering Miner")
        if api[1] != self.mode:
            logger.error("The API mode mismatch the miner mode")

        if self.mode == "getter":
            self._file_ids_to_tweets_in_json(self, api, self.input_file_path)

        elif self.mode == "stream":
            if self._output == "console":
                logger.debug(f"The output mode is set to '{self._output}'")
                stream = Stream(api[0], self._listener(self._output))
                stream.filter(
                    track=self.keywords, locations=self.locations, is_async=True
                )
            elif self._output == "file":
                logger.info(
                    "Start mining in 'stream' mode, into {file}",
                    file=self.output_file_path,
                )
                file = open(self.output_file_path, "a+")
                stream = Stream(api[0], self._listener(self._output, file=file))
                stream.filter(
                    track=self.keywords, locations=self.locations, is_async=True
                )
            elif self._output == "database":
                logger.info("Start mining in 'stream' mode into the database.")
                stream = Stream(
                    api[0], self._listener(self._output, config=self.config)
                )
                stream.filter(
                    track=self.keywords, locations=self.locations, is_async=True
                )

        else:
            logger.error("The 'mode' argument provided to the miner is invalid.")
            logger.error("It should be 'getter' or 'stream")

    def search(self, *args) -> None:
        logger.info("Entering search arguments definition")
        if self.mode != "stream":
            logger.error("Invalid 'mode' :: Mode should be 'stream'")
        for elt in args:
            if type(elt) == str:
                self.keywords.append(elt)
            elif type(elt) == list and len(elt) == 4:
                self.locations.append(elt)
            else:
                logger.error("Invalid keywords or locations provided to .search()")

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

    @staticmethod
    def _new_file_name(self, dir_name: str, extension: str) -> Path:
        """Provide the path of a new file using the parent dir name.
        
        Arguments:
            dir_name {Path} -- The path of the targeted dir.
            extension {str} -- The extension of the new file.
        
        Returns:
            output_path {Path} -- The new path generated.
        """
        dir_path = Path(dir_name)
        new_name = Path.joinpath(*Path(self.input_file_path).splitall()[-2:-1])
        output_path = dir_name / new_name + extension
        return output_path

    @staticmethod
    @logger.catch()
    def _listener(output_mode, file=None, config=None):
        logger.debug(f"Output mode is set on {output_mode}")
        if output_mode == "console":
            logger.info("ListenerConsole picked")
            return ListenerConsole()
        elif output_mode == "file":
            logger.info("ListenerFile picked")
            return ListenerFile(file)
        elif output_mode == "database":
            logger.info("ListenerDB picked")
            logger.info("Config used: {config}", config=config)
            return ListenerDB(config)
        else:
            raise ValueError("Invalid output mode passed.")


def extract_ids(path):
    tweet_ids = list()
    with open(path, "r") as file_to_extract_ids:
        for line in file_to_extract_ids:
            tweet_id = re.search(r"\d{18}", line)
            if tweet_id:
                tweet_ids.append(tweet_id.group(0))
    return tweet_ids


class ListenerConsole(StreamListener):
    def __init__(self, api=None):
        StreamListener.__init__(self, api)
        self.index_RT: int = 0

    @logger.catch()
    def on_status(self, status):
        # if status.text[:2] == "RT":
        #     self.index_RT += 1
        # elif status.text[:2] == "RT" and self.index_RT % 100 == 0:
        #     status = status.id_str + " :: " + status.text.replace("\n", " \\n ")
        #     print(status)
        #     print("_____________________________________________")
        #     print(self.index_RT)
        #     self.index_RT = 0
        # else:
        #     status = status.id_str + " :: " + status.text.replace("\n", " \\n ")
        #     print(status)
        if status.text[:2] == "RT":
            status = status.id_str + " :: " + status.text.replace("\n", " \\n ")
            print(status)


class ListenerFile(StreamListener):
    def __init__(self, writing_file, api=None):
        StreamListener.__init__(self, api)
        self.writing_file: Any = writing_file
        self.index: int = 0

    @logger.catch()
    def on_status(self, status):
        status = status.text.replace("\n", " \\n ")
        self.writing_file.write(status + "\n")
        self.index += 1
        if self.index % 10 == 0:
            self.writing_file.flush()

    @logger.catch()
    def on_error(self, status_code):
        logger.error(status_code)

    def on_disconnect(self, notice):
        self.writing_file.close()


class ListenerDB(StreamListener):
    def __init__(self, config, api=None):
        StreamListener.__init__(self, api)
        self.client = MongoClient(config["host"], config["port"])
        self.db = self.client[config["db"]]
        self.collection = self.db[config["collection"]]
        self.index_RT: int = 0

    @logger.catch()
    def on_status(self, status):
        if status.text[:2] == "RT" and self.index_RT % 10 != 0:
            self.index_RT += 1
        elif status.text[:2] == "RT" and self.index_RT % 10 == 0:
            post_id = self.collection.insert_one(status.text)
            self.index_RT = 0
        else:
            post_id = self.collection.insert_one(status.text)

    @logger.catch()
    def on_error(self, status_code):
        logger.error(status_code)
