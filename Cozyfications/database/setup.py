import sqlalchemy
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

from Cozyfications.database.models import Base

engine: AsyncEngine = create_async_engine("sqlite+aiosqlite:///Cozyfications/database/Cozyfications.db")
async_session = async_sessionmaker(bind=engine)


async def setup() -> None:
    """Sets up the database by creating the tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    msg: str = f"""Database is set up now!
        Database Type: {engine.url.drivername}
        File: {engine.url.database}
        Tables: {", ".join(table.name for table in Base.metadata.sorted_tables)}
        SQLAlchemy Version: {sqlalchemy.__version__}"""
    print(f"\n{msg}")


@event.listens_for(target=engine.sync_engine, identifier="connect")
def set_sqlite_pragma(dbapi_connection, _) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
