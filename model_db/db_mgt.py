import csv
import glob
import re
from itertools import islice
from typing import List

import edgedb


class ProtoDB(object):
    def __init__(self, namedb: str):
        self.namedb = namedb
        self.conn = None

    @property
    def connect(self):
        #  Connect to the database.
        try:
            if self.namedb == "":
                raise edgedb.errors.InternalServerError("Pas de nom de db renseigné.")
            conn = edgedb.connect(
                "edgedb://edgedb@localhost/" + self.namedb,
                user="edgedb",
                password="12345",
            )
            self.conn = conn
        except (edgedb.errors.InternalServerError, TypeError) as e:
            print(e)

    @property
    def close(self):
        self.conn.close()
        if self.conn.is_closed():
            print("Connection fermée avec succès")

    @property
    def init(self):
        # Create the model.
        self.conn.execute(
            """
        CREATE TYPE Tweet {
            CREATE REQUIRED PROPERTY tweet_id -> int64;
            CREATE REQUIRED PROPERTY tweet_text -> str;
        };
        """
        )
        self.conn.execute(
            """
            CREATE TYPE Data {
                CREATE REQUIRED LINK tweet -> Tweet;
                CREATE PROPERTY data_source -> str;
                CREATE PROPERTY info_source -> str;
                CREATE PROPERTY info_type -> str;
                CREATE PROPERTY info_rmativeness -> str;
            };
        """
        )

    def insert(
        self,
        tweet_id: int,
        tweet_text: str,
        data_source: str,
        info_source: str,
        info_type: str,
        info_rmativeness: str,
    ):
        # Insert a new Tweet.
        self.conn.fetchall(
            """ INSERT Data {
                tweet := (
                    INSERT Tweet {
                        tweet_id := <int64>$tweet_id,
                        tweet_text := <str>$tweet_text,
                    }
                ),
                data_source := <str>$data_source,
                info_source := <str>$info_source,
                info_type := <str>$info_type,
                info_rmativeness := <str>$info_rmativeness,
            }
        """,
            tweet_id=tweet_id,
            tweet_text=tweet_text,
            data_source=data_source,
            info_source=info_source,
            info_type=info_type,
            info_rmativeness=info_rmativeness,
        )

    def select_data(self):
        data_set = self.conn.fetchall(
            """SELECT Data {
                tweet: {
                    tweet_id,
                    tweet_text,
                },
                data_source,
                info_source,
                info_type,
                info_rmativeness,
            }
        """
        )
        print(data_set)

    def select_tweet(self):
        tweet_set = self.conn.fetchall(
            """SELECT Tweet {
                tweet_id,
                tweet_text,
            }
        """
        )
        print(tweet_set)


def retrieve_csvs(path_to_dir: str) -> List[str]:
    paths = glob.glob(path_to_dir, recursive=True)
    return paths


def event_name(path: str) -> str:
    pattern = re.compile(r"(_\w+)")
    event_name = pattern.findall(path)[0][1:]
    return event_name


def insert_from_T26(path: str):
    paths = retrieve_csvs(path)
    db_instance = ProtoDB("tweet1")
    db_instance.connect

    try:
        db_instance.init
    except edgedb.errors.SchemaError:
        pass

    for path in paths:
        with open(path, newline="") as csvfile:
            csv_reader = csv.reader(csvfile)
            flag = 1
            for (
                tweet_id,
                tweet_text,
                info_source,
                info_type,
                info_rmativeness,
            ) in islice(csv_reader, 1, None):
                db_instance.insert(
                    int(tweet_id),
                    tweet_text,
                    event_name(path),
                    info_source,
                    info_type,
                    info_rmativeness,
                )
                flag += 1

    db_instance.close


if __name__ == "__main__":
    insert_from_T26("/home/julien/Documents/CrisisLexT26/**/*labeled.csv")
