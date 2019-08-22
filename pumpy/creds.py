#  coding: utf-8

from loguru import logger
from tweepy.auth import AppAuthHandler, OAuthHandler
from tweepy import API


class AuthApi(object):
    def __init__(
        self,
        mode: str,
        access_token: str,
        access_token_secret: str,
        api_key: str = "",
        api_key_secret: str = "",
    ):
        self.mode = mode
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.api_key = api_key
        self.api_key_secret = api_key_secret

    @property
    def generate_api(self) -> API:
        if self.mode == "get":
            if (
                self.access_token
                and self.access_token_secret
                and (self.api_key == False or self.api_key_secret == False)
            ):
                logger.debug("Get - AppAuth")
                auth = AppAuthHandler(self.access_token, self.access_token_secret)

            elif (
                self.access_token
                and self.access_token_secret
                and self.api_key
                and self.api_key_secret
            ):
                logger.debug("Get - OAuth")
                auth = OAuthHandler(
                    self.access_token, self.access_token_secret
                ).set_access_token(self.api_key, self.api_key_secret)

            else:
                raise ValueError("Invalid credentials")

        elif self.mode == "stream":
            if (
                self.access_token
                and self.access_token_secret
                and self.api_key
                and self.api_key_secret
            ):
                logger.debug("Stream - OAuth")
                auth = OAuthHandler(
                    self.access_token, self.access_token_secret
                ).set_access_token(self.api_key, self.api_key_secret)

            else:
                raise ValueError("Invalid credentials")
        else:
            raise ValueError("The 'mode' argument should be 'stream' or 'get'")

        return API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
