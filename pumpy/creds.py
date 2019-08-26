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
                auth.set_token(self.key, self.key_secret)

            else:
                raise ValueError("Invalid credentials")

            return (auth, self.mode)
        else:
            raise ValueError("The 'mode' argument should be 'stream' or 'getter'")


if __name__ == "__main__":
    api1 = AuthApi(
        mode="getter",
        token="pUhieXUga8cOYhAd9aVrTwljM",
        token_secret="w1XVYYdctDpEuvg3e7xZNYU1CweUNZGRsnhIBybRDCa4mpv3N8",
        key="981955283676254208-VEhPUugVV6pCSUIp4C8Sfl641DNPAyo",
        key_secret="ItEustxX9YMaDACmNHFWXFjE8LbkXPVFxFBUNHocrqyCy",
    ).generate_api
    api2 = AuthApi(mode="stream", token="", token_secret="")
    api3 = AuthApi(mode="getter", token="", token_secret="")
    print(type(api1[0]))
    print(api2)
    print(api3)
