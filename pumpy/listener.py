# coding: utf-8

from loguru import logger
from typing import Tuple, List, Any
import tweepy
from tweepy import API, OAuthHandler, StreamListener
from pymongo import MongoClient


class _ListenerBot(StreamListener):
    def __init__(self, auth_keys, auth_idx):
        self.DEBUG = True
        self.auth_keys = auth_keys
        self.auth_idx = auth_idx
        self.api: Tuple[OAuthHandler, str] = API(
            self.auth_keys[self.auth_idx]._generate_api[0]
        )

        self._message = (
            "Hello @{}, we are a group of researchers at Penn State IST, we are researching ways to "
            "locate people via social media during emergency events. Please take this 1-minute survey "
            "at https://pennstate.qualtrics.com/jfe/form/SV_9to3KUIthUvQ473?TwitterScreenName={}"
        )

    @logger.catch()
    def on_status(self, status):
        user: str = status.user.screen_name
        logger.debug("Tweet found!")
        self._send_message("Julien")

    @logger.catch()
    def _send_message(self, screen_name: List[str]) -> None:
        """
        Send a direct message to the user and if
        :param screen_names: list of strings for the screen names that you want to sent a message to
        :return: None
        """
        logger.info("Entering send message")
        # find the users by their screen name
        # TODO this may throw an exception other than rate limit
        try:
            user = self.api.lookup_users(screen_names=screen_name)
            tweet_at = False
            try:
                message = self.api.send_direct_message(
                    recipient_id=user[1].id,
                    text=self._message.format(user[1].screen_name, user[1].screen_name),
                )
                if self.DEBUG:
                    self.api.destroy_direct_message(message.id)
            except tweepy.error.TweepError as ex:
                # couldn't send them a DM so flip the flag
                if ex.api_code == 349:
                    tweet_at = True
                # hit the rate limit
                elif tweepy.error.is_rate_limit_error_message(ex):
                    # try to switch accounts
                    self._auth_next_account()
                else:
                    print(ex)
            if tweet_at:
                tweet = self.api.update_status(
                    self._message.format(user[1].screen_name, user[1].screen_name)
                )
                if self.DEBUG:
                    self.api.destroy_status(tweet.id)
        except tweepy.error.RateLimitError:
            # try to switch accounts
            self._auth_next_account()

    def _auth_next_account(self) -> tweepy.API:
        """
        Internal function that shouldn't be called outside of send_messages, it tries to
        grab the next account and if it reaches the end, it wraps back around to the
        first set of keys.

        :return: the new api, but it also sets self.api so unnecessary
        """
        self.auth_idx = self.auth_idx + 1
        if len(self.auth_keys) <= self.auth_idx:
            self.auth_idx = 0

        self.api = self.auth_keys[self.auth_idx]._generate_api[0]


class _ListenerConsole(StreamListener):
    def __init__(self, sample=15, api=None, to_console=False):
        StreamListener.__init__(self, api)
        self.index_RT: int = 1
        self.sample: int = sample
        self.to_console: bool = to_console

    @logger.catch()
    def on_status(self, status) -> None:
        if self.to_console:
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


class _ListenerFile(StreamListener):
    def __init__(self, writing_file, sample=15, api=None):
        StreamListener.__init__(self, api)
        self.writing_file: Any = writing_file
        self.sample = sample
        self.index_RT: int = 0

    @logger.catch()
    def on_status(self, status):
        if status.text[:2] == "RT" and self.index_RT % self.sample != 0:
            self.index_RT += 1
        elif status.text[:2] == "RT" and self.index_RT % self.sample == 0:
            status = status.id_str + " :: " + status.text.replace("\n", " \\n ")
            self.writing_file.write(status + "\n")
            self.index_RT = 1
        else:
            status = status.id_str + " :: " + status.text.replace("\n", " \\n ")
            self.writing_file.write(status + "\n")

        self.index_RT += 1
        if self.index_RT % 10 == 0:
            self.writing_file.flush()

    @logger.catch()
    def on_error(self, status_code):
        logger.error(status_code)

    def on_disconnect(self, notice):
        self.writing_file.close()


class _ListenerDB(StreamListener):
    def __init__(self, config, sample=15, api=None):
        StreamListener.__init__(self, api)
        self.client = MongoClient(config["host"], config["port"])
        self.db = self.client[config["db"]]
        self.collection = self.db[config["collection"]]
        self.sample = sample
        self.index_RT: int = 1

    @logger.catch()
    def on_status(self, status):
        if status.text[:2] == "RT" and self.index_RT % self.sample != 0:
            self.index_RT += 1
        elif status.text[:2] == "RT" and self.index_RT % self.sample == 0:
            post_id = self.collection.insert_one(status._json)
            self.index_RT = 1
        else:
            post_id = self.collection.insert_one(status._json)

    @logger.catch()
    def on_error(self, status_code):
        logger.error(status_code)
