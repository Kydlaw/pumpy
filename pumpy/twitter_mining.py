import csv
import json
import re
import typing
from typing import List

import tweepy
from loguru import logger
from path import Path
from tweepy import OAuthHandler

from utils.utils import new_file_name
from .creds import access_secret, access_token, consumer_key, consumer_secret


LOGGER_ROOT = "/home/julien/Doctorat/Code/Proto/logs/"

CONSUMMER_KEY = consumer_key
CONSUMMER_SECRET = consumer_secret
ACCESS_TOKEN = access_token
ACCESS_SECRET = access_secret

auth = OAuthHandler(CONSUMMER_KEY, CONSUMMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


def file_ids_to_tweets_in_json(path_str_tweet_ids_csv: str) -> None:
    path_tweet_ids_csv: Path = Path(path_str_tweet_ids_csv)
    logger.add(LOGGER_ROOT + str(path_tweet_ids_csv.dirname().basename()) + ".log")
    ids: List[str] = list()
    with open(path_tweet_ids_csv, "r", encoding="utf-8") as ids_csv:
        csv_reader = csv.reader(ids_csv)
        for line in csv_reader:
            ids.append(line[1])

    path_tweet_json = new_file_name(path_tweet_ids_csv, extension=".json")
    write_tweets_through_ids(ids, path_tweet_json)


def write_tweets_through_ids(list_ids: List[str], path_tweet_json: Path) -> None:
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
