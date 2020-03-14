#  coding: utf-8

from loguru import logger
from tweepy import API, OAuthHandler


class AuthApi(API):
    """
    Generate a Tweepy AuthHandler object that will be used later to generate an API.

    Arguments:
        access_token {str} -- Access access_token
        access_token_secret {str} -- Access access_token secret
        consumer_api_key {str} -- Consumer API consumer_api_key
        consumer_api_secret {str} -- Consumer API consumer_api_key secret
    """

    def __init__(
        self,
        access_token: str,
        access_token_secret: str,
        consumer_api_key: str = "",
        consumer_api_secret: str = "",
    ):
        super().__init__()
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.consumer_api_key = consumer_api_key
        self.consumer_api_secret = consumer_api_secret

    @property
    def generate_api(self) -> OAuthHandler:
        """
        Use the credentials passed during initialization to generate an OAuthHandler.
        It will then be used later to generate an API object to request Twitter's API.
        
        Raises:
            ValueError: Missing credentials
        
        Returns:
            OAuthHandler -- [description]
        """
        if (
            self.consumer_api_key
            and self.consumer_api_secret
            and self.access_token
            and self.access_token_secret
        ):
            logger.debug("Creation OAuthHandler")
            auth = OAuthHandler(self.consumer_api_key, self.consumer_api_secret)
            auth.set_access_token(self.access_token, self.access_token_secret)
        else:
            raise ValueError("Missing credentials")
        return auth
