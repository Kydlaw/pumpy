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


def main2():
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


if __name__ == "__main__":
    main2()
