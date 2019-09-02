#  coding: utf-8

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
        token {str} -- Access token
        token_secret {str} -- Access token secret
        key {str} -- Consumer API key
        key_secret {str} -- Consumer API key secret
    
    Raises:
        ValueError: Invalid credentials
        ValueError: The 'mode' argument should be 'stream' or 'getter'
    
    Returns:
        [API] -- A Tweepy's API object
    """

    def __init__(
        self,
        mode: str,
        token: str,
        token_secret: str,
        key: str = "",
        key_secret: str = "",
    ):
        super().__init__()
        self.mode = mode
        self.token = token
        self.token_secret = token_secret
        self.key = key
        self.key_secret = key_secret

    @property
    def generate_api(self) -> API:
        if self.mode == "getter":
            if (
                self.token
                and self.token_secret
                and (self.key == False or self.key_secret == False)
            ):
                logger.debug("Getter - AppAuth")
                auth = AppAuthHandler(self.token, self.token_secret)

            elif self.token and self.token_secret and self.key and self.key_secret:
                logger.debug("Getter - OAuth")
                auth = OAuthHandler(self.token, self.token_secret)
                auth.set_access_token(self.key, self.key_secret)

            else:
                raise ValueError("Invalid arguments")

            return (
                API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True),
                self.mode,
            )

        elif self.mode == "stream":
            if self.token and self.token_secret and self.key and self.key_secret:
                logger.debug("Stream - OAuth")
                auth = OAuthHandler(self.token, self.token_secret)
                auth.set_access_token(self.key, self.key_secret)

            else:
                raise ValueError("Invalid credentials")

            return (auth, self.mode)
        else:
            raise ValueError("The 'mode' argument should be 'stream' or 'getter'")
