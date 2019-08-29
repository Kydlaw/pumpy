import edgedb


class ProtoDB(object):
    def __init__(self, namedb: str):
        self.namedb = namedb
        self.conn: edgedb.Connec = None

    def connect(self, user, password):
        #  Connect to the database.
        try:
            if self.namedb == "":
                raise edgedb.errors.InternalServerError("Pas de nom de db renseigné.")
            conn = edgedb.connect(
                "edgedb://edgedb@localhost/" + self.namedb, user=user, password=password
            )
            self.conn = conn
        except (edgedb.errors.InternalServerError, TypeError) as e:
            print(e)

    @property
    def close(self) -> None:
        self.conn.close()
        if self.conn.is_closed():
            print("Connection fermée avec succès")

    @property
    def init(self) -> None:
        """Create the database model. (EdgeDB)"""
        self.conn.execute(
            """
            CREATE TYPE Tweet {
                CREATE REQUIRED PROPERTY id_str -> str;
                CREATE PROPERTY text -> str;
            };
        """
        )

    def insert(self, id_str: str, text: str) -> None:
        # Insert a new Tweet.
        self.conn.fetchall(
            """
            INSERT Tweet {
                id_str := <str>$id_str,
                text := <str>$text,
            }
        """,
            id_str=id_str,
            text=text,
        )

    def select(self):
        tweet_set = self.conn.fetchall(
            """SELECT Tweet {
                tweet_id,
                tweet_text,
            }
        """
        )
        print(tweet_set)


def main():
    db_instance = ProtoDB("test")
    db_instance.connect
    db_instance.init


if __name__ == "__main__":
    main()
