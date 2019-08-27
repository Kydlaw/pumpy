import csv
import json
import re
import typing
from typing import List

import tweepy
from loguru import logger
from path import Path
from tweepy import API, Stream, StreamListener

from .creds import AuthApi

LOGGER_ROOT = "./logs/"


class Miner(object):
    def __init__(self, mode: str):
        self.mode = mode
        self.input_file_path = None
        self.output_file_path = None
        self.index_ids = 0
        self.keywords: List[str] = list()
        self.locations: List[List[int]] = list()

    def from_file(self, path_input_file: str, index_ids: int) -> "Miner":
        path = Path(path_input_file)
        if not path.exists():
            raise FileNotFoundError("Wrong file or file path")
        if self.mode == "getter":
            self.input_file_path = Path(path)
            self.index_ids = index_ids
            return self
        else:
            raise ValueError("from_file() method is only available in 'getter' mode")

    def to(self, output) -> None:
        """Define where the data will be sent. It can be stdout, in a file or in a database
        
        Arguments:
            output {str} -- Path toward the directory where the data will be stored.
        
        Raises:
            NotImplementedError: pass
            ValueError: Raised in getter mode if no file was given through from_file()
        
        Returns:
            Path -- Path object toward the file where the data will be stored.
        """
        if output == "database":
            raise NotImplementedError
        else:
            if self.mode == "getter" and self.input_file_path is None:
                raise ValueError("Please define input file before calling to()")
            output_path = Path(output)
            self.output_file_path = self._new_file_name(
                self, output_path, extension=".json"
            )

    def mine(self, api: tuple):
        # Todo: Add a valid logger -> logger.add(LOGGER_ROOT + str(path_tweet_ids_csv.dirname().basename()) + ".log")
        if api[1] != self.mode:
            raise ValueError("The API mode mismatch the miner mode")

        if self.mode == "getter":
            self._file_ids_to_tweets_in_json(self, api, self.input_file_path)

        elif self.mode == "stream":
            # TODO: Create a Stream with the correct config
            # TODO: Call filter with the right parameters
            raise NotImplementedError

        else:
            raise ValueError(
                "The 'mode' argument is not valid. It should be 'getter' or 'stream'"
            )

    def search(self, *args) -> None:
        if self.mode != "stream":
            raise ValueError("Invalid mode. Mode should be 'stream'.")
        for elt in args:
            if type(elt) == str:
                self.keywords.append(elt)
            elif type(elt) == list and len(elt) == 4:
                self.locations.append(elt)
            else:
                raise ValueError("Invalid argument type")

    def db_config(self):
        raise NotImplementedError

    @staticmethod
    def _write_tweets_through_ids(
        api: API, list_ids: List[str], path_tweet_json: Path
    ) -> None:
        tweets: List[str] = list()
        with open(str(path_tweet_json), "a+", encoding="utf-8") as resulting_json:
            for tweet_id in list_ids:
                try:
                    tweet = api.get_status(tweet_id)._json
                except tweepy.error.TweepError as err:
                    pass
                    # Todo logger.warning(f"{tweet_id} | {err}")
                else:
                    # Todo logger.info(f"OK")
                    tweets.append(tweet)

            json.dump(tweets, resulting_json, ensure_ascii=False, indent=4)

    @staticmethod
    def _file_ids_to_tweets_in_json(self, api: API, path_tweet_ids_csv: Path) -> None:
        # Todo: yield directement les ids au lieu de créer une liste
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
        if "." not in extension:
            raise SyntaxError("Missing '.' character in the extension name")
        dir_path = Path(dir_name)
        new_name = Path.joinpath(*Path(self.input_file_path).splitall()[-2:-1])
        output_path = dir_name / new_name + extension
        return output_path


def extract_ids(path):
    tweet_ids = list()
    with open(path, "r") as file_to_extract_ids:
        for line in file_to_extract_ids:
            tweet_id = re.search(r"\d{18}", line)
            if tweet_id:
                tweet_ids.append(tweet_id.group(0))
    return tweet_ids


def _listener(self):
    class Listener(StreamListener):
        def on_status(self, status):
            print(status.text)

        def on_error(self, status):
            print(status)

    return Listener()
