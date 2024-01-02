import json

from mysql import connector
from mysql.connector.abstracts import MySQLCursorAbstract

from Cozyfications.secrets import Database

schemas = [
    "CREATE SCHEMA `cozyfications` DEFAULT CHARACTER SET utf8mb4"
]

tables = [
    """CREATE TABLE `cozyfications`.`twitch` (
        `guild_id` BIGINT NOT NULL,
        `streamers` JSON NULL,
        `message` TEXT,
        `channel` BIGINT,
        PRIMARY KEY (`guild_id`),
        UNIQUE INDEX `guild_id_UNIQUE` (`guild_id` ASC) VISIBLE
    )""",
    """CREATE TABLE `cozyfications`.`messages` (
        `message_id` BIGINT NOT NULL,
        `guild_id` BIGINT NULL,
        `streamer` BIGINT NULL,
        `channel_id` BIGINT NULL,
        PRIMARY KEY (`message_id`),
        UNIQUE INDEX `message_id_UNIQUE` (`message_id` ASC) VISIBLE
    )""",
    """CREATE TABLE `cozyfications`.`subscriptions` (
        `streamer` BIGINT NOT NULL,
        `guild_id` BIGINT NOT NULL,
        `subscription_id` LONGTEXT NOT NULL
    )"""
]


class Result:
    def __init__(self, cursor: MySQLCursorAbstract):
        self._cur = cursor
        self.rows = cursor.rowcount

    @property
    def value(self):
        fetch = self._cur.fetchone()
        if fetch is not None and fetch[0] is not None:
            if type(fetch[0]) in [dict, list, tuple] or (type(fetch[0]) is str and str(fetch[0])[0] in "{}[]"):
                return json.loads(fetch[0])
            else:
                return fetch[0]
        else:
            return None

    @property
    def value_all_raw(self):
        return self._cur.fetchall()

    @property
    def value_all(self):
        fetch = self._cur.fetchall()
        if not fetch is None:
            return [i[0] if len(i) == 1 else list(i) for i in fetch]
        return []


def connect():
    try:
        return connector.connect(
            host=Database.HOST,
            port=Database.PORT,
            user=Database.USER,
            passwd=Database.PASSWORD,
            use_unicode=True
        )
    except Exception as e:
        quit(f"Couldn't connect to DB: {e}")


def cursor(db):
    try:
        return db.cursor(buffered=True)
    except Exception as e:
        quit(f"Couldn't connect to DB's cursor: {e}")


def create():
    db = connect()
    cur = cursor(db)

    print("Creating schemas...")
    for i in schemas:
        schema = i.split("`")[1]
        try:
            (cur.execute(i), db.commit(), print(f"  Created schema '{schema}'"))
        except Exception as e:
            print(f"  Error creating schema '{schema}': {e}")

    print("Creating tables...")
    for i in tables:
        table = i.split("`")[3]
        try:
            (cur.execute(i), db.commit(), print(f"  Created table '{table}'"))
        except Exception as e:
            print(f"  Error creating table '{table}': {e}")

    cur.close()
    del cur


def select(q):
    db = connect()
    cur = cursor(db)

    cur.execute(q)
    return Result(cur)


def update(q):
    db = connect()
    cur = cursor(db)

    cur.execute(q)
    db.commit()
    cur.close()
    del cur


def delete(table, guild_id):
    db = connect()
    cur = cursor(db)

    cur.execute(
        f"""DELETE FROM `{table}`
        WHERE guild_id = `{guild_id}`"""
    )
    db.commit()
    cur.close()
    del cur
