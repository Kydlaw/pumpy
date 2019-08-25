import csv
import json
import re
import typing
from typing import List

import tweepy
from loguru import logger
from path import Path
from tweepy import API

from .creds import AuthApi

LOGGER_ROOT = "./logs/"


class Miner(object):
    def __init__(self, mode: str):
        self.mode = mode
        self.status = False
        self.output_file = None
        self.input_file = None

    def from_file(self, path_input_file: str, index_ids: int) -> "Miner":
        self.input_file = Path(path_input_file)
        self.index_ids = index_ids
        return self

    def to(self, output) -> None:
        if output == "database":
            raise NotImplementedError
        else:
            if self.input_file is None:
                raise ValueError("Please define input file before calling to()")
            output_path = Path(output)
            self.output_file = _new_file_name(output_path, extension=".json")

    def mine(self, api: API):
        # Todo: Perform check of API's mode
        # Todo: Add a valid logger -> logger.add(LOGGER_ROOT + str(path_tweet_ids_csv.dirname().basename()) + ".log")
        if self.mode == "getter":
            _file_ids_to_tweets_in_json(api, self.input_file)
        elif self.mode == "stream":
            raise NotImplementedError
        else:
            raise ValueError(
                "The 'mode' argument is not valid. It should be 'getter' or 'stream'"
            )

    def db_config(self):
        raise NotImplementedError

    def _write_tweets_through_ids(
        self, api: API, list_ids: List[str], path_tweet_json: Path
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

    def _file_ids_to_tweets_in_json(api: API, path_tweet_ids_csv: Path) -> None:
        # Todo: yield directement les ids au lieu de créer une liste
        ids: List[str] = list()
        with open(path_tweet_ids_csv, "r", encoding="utf-8") as ids_csv:
            csv_reader = csv.reader(ids_csv)
            for line in csv_reader:
                ids.append(line[index_ids])

        _write_tweets_through_ids(api, ids, output_file)

    def _new_file_name(input_path: Path, extension: str) -> Path:
        """Provide the path of a new file using the parent dir name.
        
        Arguments:
            input_path {Path} -- The path of a file contained in the targeted dir
            extension {str} -- The extension of the new file
        
        Returns:
            output_path {Path} -- The new path generated
        """
        if "." not in extension:
            raise SyntaxError("Missing '.' character in the extension name")
        output_path: Path = Path(
            Path.joinpath(*input_path.splitall()[:-1])
        ) / input_path.dirname().basename() + extension
        return output_path


def extract_ids(path):
    tweet_ids = list()
    with open(path, "r") as file_to_extract_ids:
        for line in file_to_extract_ids:
            tweet_id = re.search(r"\d{18}", line)
            if tweet_id:
                tweet_ids.append(tweet_id.group(0))
    return tweet_ids
