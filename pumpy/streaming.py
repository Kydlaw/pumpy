from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream, API
import tweepy
import json


class Listener(StreamListener):
    def on_status(self, status):
        print(status.text)

    def on_error(self, status):
        print(status)


if __name__ == "__main__":
    l = Listener()
    auth = OAuthHandler(
        "pUhieXUga8cOYhAd9aVrTwljM",
        "w1XVYYdctDpEuvg3e7xZNYU1CweUNZGRsnhIBybRDCa4mpv3N8",
    )
    auth.set_access_token(
        "981955283676254208-VEhPUugVV6pCSUIp4C8Sfl641DNPAyo",
        "ItEustxX9YMaDACmNHFWXFjE8LbkXPVFxFBUNHocrqyCy",
    )

    stream = Stream(auth, l)

    stream.filter(
        locations=[2.0093369554, 43.8595698047, 2.2891864074, 44.0104129104],
        is_async=True,
    )

