import json

from mysql import connector
from mysql.connector.abstracts import MySQLCursorAbstract

from Cozyfications.secrets import Database

schemas = [
    "CREATE SCHEMA `cozyfications` DEFAULT CHARACTER SET utf8mb4"
]

tables = [
    """CREATE TABLE `cozyfications`.`twitch` (
        `guildid` BIGINT NOT NULL,
        `streamers` JSON NULL,
        `message` TEXT,
        `channel` BIGINT,
        PRIMARY KEY (`guildid`),
        UNIQUE INDEX `guildid_UNIQUE` (`guildid` ASC) VISIBLE
    )""",
    """CREATE TABLE `cozyfications`.`messages` (
        `messageid` BIGINT NOT NULL,
        `guildid` BIGINT NULL,
        `streamer` BIGINT NULL,
        `channelid` BIGINT NULL,
        PRIMARY KEY (`messageid`),
        UNIQUE INDEX `messageid_UNIQUE` (`messageid` ASC) VISIBLE
    )""",
    """CREATE TABLE `cozyfications`.`subscriptions` (
        `streamer` BIGINT NOT NULL,
        `guildid` BIGINT NOT NULL,
        `subid` LONGTEXT NOT NULL
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
        fetch = self._cur.fetchall()
        if fetch is not None:
            ret = []
            for i in fetch:
                ret.append(i[0])
            return ret
        else:
            return None

    @property
    def value_all(self):
        fetch = self.value_all_raw
        if fetch is not None:
            ret = []
            for i in fetch:
                if i not in ret:
                    ret.append(i)
            return ret
        else:
            return None


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


def delete(table, guildid):
    db = connect()
    cur = cursor(db)

    cur.execute(
        f"""DELETE FROM `{table}`
        WHERE guildid = `{guildid}`"""
    )
    db.commit()
    cur.close()
    del cur
