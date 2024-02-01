from sqlalchemy import event, create_engine, Engine

engine: Engine = create_engine("sqlite:///Cozyfications/database/Cozyfications.db")


@event.listens_for(target=engine, identifier="connect")
def set_sqlite_pragma(dbapi_connection, _) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
