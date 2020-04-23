# coding: utf-8

import os

from pumpy.twitter_mining import MinerStream
from pumpy.authapi import AuthApi

############################ THINGS TO CHANGE ############################
# - Set your Twitter's access tokens/keys as environment variables (in your .zshrc or
# activate file of your python virtual environment)
# OR remove the "os.environ.get("...") and copy/paste your tokens/keys as strings
# - (Optional) You can change the db's name and collection's name in the .db_config
# (mine are "tweets" and "covid" for example)
# - The keywords are defined in .search(...). The format is commat separated strings.


def main():
    miner = MinerStream()
    miner.auth_keys.append(
        AuthApi(
            access_token=os.environ.get("ACCESS_TOKEN"),
            access_token_secret=os.environ.get("ACCESS_SECRET"),
            consumer_api_key=os.environ.get("CONSUMER_KEY"),
            consumer_api_secret=os.environ.get("CONSUMER_SECRET"),
        )
    )

    miner.to("database").db_config(db="tweets", collection="covid3")
    # miner.search("hand sanitizer", "out of", "not flu", "COVID19", "test kit")
    # miner.search("hand sanitizer", "out of", "not flu", "COVID19", "test kit", "stay home", "quarantine", "lockdown") fin 19:03
    miner.search(
        "hand sanitizer",
        "out of",
        "not flu",
        "COVID19",
        "test kit",
        "stay home",
        "quarantine",
        "lockdown",
        "PSH",
        "cough",
        "fever",
        "breath",
        "chest",
        "infected",
        "contaminated",
        "pandemic",
    )

    miner.mine()


if __name__ == "__main__":
    main()
