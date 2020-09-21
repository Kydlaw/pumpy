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


def main_stream():
    miner = MinerStream()
    miner.auth_keys.append(
        AuthApi(
            # access_token=os.environ.get("ACCESS_TOKEN"),
            # access_token_secret=os.environ.get("ACCESS_SECRET"),
            # consumer_api_key=os.environ.get("CONSUMER_KEY"),
            # consumer_api_secret=os.environ.get("CONSUMER_SECRET"),
            access_token="1192128601858158593-T2hfRkPduwGGM8iV6wd8503OYu0U49",
            access_token_secret="IWveNVyykSMmhWKYvGNeotl6PpE0BGijsSlvzjalezotH",
            consumer_api_key="AvH9eihMAIfBIzcEN0N1WhXpi",
            consumer_api_secret="NhMhfyxM4e6E4wquRkRhna0aGmUV8IfTWhEitiAIJnrpsIQTkl",
        )
    )

    miner.to("database").db_config(db="test", collection="geopsu")
    # miner.search("covid")
    miner.search((-77.9822, 40.7349, -77.7127, 40.8533))

    miner.mine()


if __name__ == "__main__":
    main_stream()
