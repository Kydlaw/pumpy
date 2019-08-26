#  coding: utf-8

from pumpy.twitter_mining import Miner

miner1 = Miner("getter")
miner1.from_file("/home/kyd/Code/pumpy/data/Colorado_wildfire/Colorado_ids.csv", 1).to(
    "/home/kyd/Code/pumpy/data/Colorade_wildfire/Colorado_ids.csv"
)
print(miner1)
print(miner1.input_file)
print(miner1.index_ids)
print(miner1.output_file_path)
