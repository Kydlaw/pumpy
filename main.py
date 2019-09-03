#  coding: utf-8

from pumpy.twitter_mining import Miner
from pumpy.creds import AuthApi


def main1():
    miner1 = Miner("getter")
    miner1.from_file(
        "/home/kyd/Code/pumpy/data/Colorado_wildfire/Colorado_ids.csv", 1
    ).to("/home/kyd/Code/pumpy/data/Colorade_wildfire/Colorado_ids.csv")
    print(miner1)
    print(miner1.input_file)
    print(miner1.index_ids)
    print(miner1.output_file_path)


def stream2file():
    api = AuthApi(
        "stream",
        token="pUhieXUga8cOYhAd9aVrTwljM",
        token_secret="w1XVYYdctDpEuvg3e7xZNYU1CweUNZGRsnhIBybRDCa4mpv3N8",
        key="981955283676254208-VEhPUugVV6pCSUIp4C8Sfl641DNPAyo",
        key_secret="ItEustxX9YMaDACmNHFWXFjE8LbkXPVFxFBUNHocrqyCy",
    ).generate_api
    miner = Miner("stream")
    miner.to("/home/kyd/Code/pumpy/data/tweets/")
    miner.search("banane")
    miner.mine(api)


def stream2db():
    api = AuthApi(
        "stream",
        token="pUhieXUga8cOYhAd9aVrTwljM",
        token_secret="w1XVYYdctDpEuvg3e7xZNYU1CweUNZGRsnhIBybRDCa4mpv3N8",
        key="981955283676254208-VEhPUugVV6pCSUIp4C8Sfl641DNPAyo",
        key_secret="ItEustxX9YMaDACmNHFWXFjE8LbkXPVFxFBUNHocrqyCy",
    ).generate_api
    miner = Miner("stream")
    miner.to("database").db_config()
    miner.search("fire", "flood", "tornado", "Dorian")
    miner.mine(api)


def stream2raw():
    api = AuthApi(
        "stream",
        token="pUhieXUga8cOYhAd9aVrTwljM",
        token_secret="w1XVYYdctDpEuvg3e7xZNYU1CweUNZGRsnhIBybRDCa4mpv3N8",
        key="981955283676254208-VEhPUugVV6pCSUIp4C8Sfl641DNPAyo",
        key_secret="ItEustxX9YMaDACmNHFWXFjE8LbkXPVFxFBUNHocrqyCy",
    ).generate_api
    miner = Miner("stream")
    miner.to("console")
    miner.search("gay", "islam", "trump", "raciste", "cul")
    miner.mine(api)


def getter():
    api = AuthApi(
        "getter",
        token="pUhieXUga8cOYhAd9aVrTwljM",
        token_secret="w1XVYYdctDpEuvg3e7xZNYU1CweUNZGRsnhIBybRDCa4mpv3N8",
        key="981955283676254208-VEhPUugVV6pCSUIp4C8Sfl641DNPAyo",
        key_secret="ItEustxX9YMaDACmNHFWXFjE8LbkXPVFxFBUNHocrqyCy",
    ).generate_api
    miner = Miner("getter")
    miner.from_file(
        "/home/kyd/Code/pumpy/data/Colorade_wildfire/Colorado_ids.csv", 1
    ).to("/home/kyd/Code/pumpy/data/tweets/")
    miner.mine(api)


if __name__ == "__main__":
    stream2db()
