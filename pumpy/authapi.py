#  coding: utf-8

from typing import Tuple

from loguru import logger
from tweepy import API, Stream
from tweepy.auth import AppAuthHandler, OAuthHandler
from tweepy.streaming import StreamListener


class AuthApi(API):
    """
    Return a Tweepy's API object. Used to perform calls to Twitter's API.
    Return a different API object according to the chosen mode and the tokens provided.
    Modes :
    "getter" -> get tweets according to an ids list.
    "stream" -> stream tweets.
    
    Arguments:
        mode: {str} -- 'getter' or 'stream'
        access_token {str} -- Access access_token
        access_token_secret {str} -- Access access_token secret
        consumer_api_key {str} -- Consumer API consumer_api_key
        consumer_api_secret {str} -- Consumer API consumer_api_key secret
    
    Raises:
        ValueError: Invalid credentials
        ValueError: The 'mode' argument should be 'stream' or 'getter'
    
    Returns:
        [API] -- A Tweepy's API object
    """

    def __init__(
        self,
        mode: str,
        access_token: str,
        access_token_secret: str,
        consumer_api_key: str = "",
        consumer_api_secret: str = "",
    ):
        super().__init__()
        self.mode = mode
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.consumer_api_key = consumer_api_key
        self.consumer_api_secret = consumer_api_secret

    @property
    def _generate_api(self) -> Tuple[OAuthHandler, str]:
        if self.mode == "getter":
            if (
                self.consumer_api_key
                and self.consumer_api_secret
                and (self.access_token == False or self.access_token_secret == False)
            ):
                logger.debug("Getter - AppAuth")
                auth = AppAuthHandler(self.consumer_api_key, self.consumer_api_secret)

            elif (
                self.consumer_api_key
                and self.consumer_api_secret
                and self.access_token
                and self.access_token_secret
            ):
                logger.debug("Getter - OAuth")
                auth = OAuthHandler(self.consumer_api_key, self.consumer_api_secret)
                auth.set_access_token(self.access_token, self.access_token_secret)

            else:
                raise ValueError("Invalid arguments")

            return API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

        elif self.mode == "stream":
            if (
                self.consumer_api_key
                and self.consumer_api_secret
                and self.access_token
                and self.access_token_secret
            ):
                logger.debug("Stream - OAuth")
                auth = OAuthHandler(self.consumer_api_key, self.consumer_api_secret)
                auth.set_access_token(self.access_token, self.access_token_secret)

            else:
                raise ValueError("Invalid credentials")

            return (auth, self.mode)
        else:
            raise ValueError("The 'mode' argument should be 'stream' or 'getter'")
