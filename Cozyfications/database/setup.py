import sqlalchemy

from Cozyfications.database.engine import engine
from Cozyfications.database.models import Base


def setup() -> None:
    """Sets up the database by creating the tables."""
    Base.metadata.create_all(engine)
    msg: str = f"""Database is set up now!
        Database Type: {engine.url.drivername}
        File: {engine.url.database}
        Tables: {", ".join(table.name for table in Base.metadata.sorted_tables)}
        SQLAlchemy Version: {sqlalchemy.__version__}"""
    print(f"\n{msg}")
