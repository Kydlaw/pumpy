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
from .utils import new_file_name

LOGGER_ROOT = "./logs/"


def file_ids_to_tweets_in_json(api: API, path_str_tweet_ids_csv: str) -> None:
    path_tweet_ids_csv: Path = Path(path_str_tweet_ids_csv)
    logger.add(LOGGER_ROOT + str(path_tweet_ids_csv.dirname().basename()) + ".log")
    ids: List[str] = list()
    with open(path_tweet_ids_csv, "r", encoding="utf-8") as ids_csv:
        csv_reader = csv.reader(ids_csv)
        for line in csv_reader:
            ids.append(line[1])

    path_tweet_json = new_file_name(path_tweet_ids_csv, extension=".json")
    write_tweets_through_ids(api, ids, path_tweet_json)


def write_tweets_through_ids(
    api: API, list_ids: List[str], path_tweet_json: Path
) -> None:
    tweets: List[str] = list()
    with open(str(path_tweet_json), "a+", encoding="utf-8") as resulting_json:
        for tweet_id in list_ids:
            try:
                tweet = api.get_status(tweet_id)._json
            except tweepy.error.TweepError as err:
                logger.warning(f"{tweet_id} | {err}")
            else:
                logger.info(f"OK")
                tweets.append(tweet)

        json.dump(tweets, resulting_json, ensure_ascii=False, indent=4)


def extract_ids(path):
    tweet_ids = list()
    with open(path, "r") as file_to_extract_ids:
        for line in file_to_extract_ids:
            tweet_id = re.search(r"\d{18}", line)
            if tweet_id:
                tweet_ids.append(tweet_id.group(0))
    return tweet_ids
