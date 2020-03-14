# Pumpy
A Twitter pump, for research purpose. Build on Tweepy shoulders.

This repo provides tools to:

- Get past data from tweet ids.
- Get data through the Twitter's streaming interface.
- Convert tweets in an invalid JSON format into a valid one.

# Instructions

- Pumpy requires MongoDB for database storage (see [MongoDB install](https://docs.mongodb.com/manual/administration/install-community)
to install).
- `git clone https://github.com/Kydlaw/pumpy.git`
- Install dependancies from requirements.txt (`pip install -r requirements.txt`). Use of a python virtual
environment is prefered.
- Modify the wanted parameters in `main.py`
- Launch the script with `python main.py`
- ... should works, somehow, maybe? who knows?