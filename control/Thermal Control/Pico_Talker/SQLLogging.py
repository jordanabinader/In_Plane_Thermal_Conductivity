import asyncio
import aiosqlite
import sqlite3
import logging
import time

LOGGING_INITIALIZATION_QUERY = """
                        CREATE TABLE IF NOT EXISTS logs (
                        source TEXT NOT NULL,
                        time REAL NOT NULL,
                        lvl INTEGER,
                        lvl_name TEXT,
                        msg TEXT, 
                        name TEXT,
                        logger TEXT,
                        lineno INTEGER
                        )
                        """

class AsyncDatabaseHandler(logging.Handler):
    def __init__(self, db_file:str, loop:asyncio.AbstractEventLoop):
        super().__init__()
        self.db_file = db_file
        self.loop = loop
        asyncio.new_event_loop().run_until_complete(self.createDatabase())

    async def createDatabase(self):
        self.db = await aiosqlite.connect(self.db_file)
        await self.db.execute(LOGGING_INITIALIZATION_QUERY)
        await self.db.commit()
        

class DatabaseHandler(logging.Handler):
    def __init__(self, db_file:str, name:str):
        super().__init__()
        self.db_file = db_file
        self.name = name
        self.db = sqlite3.connect(self.db_file)
        self.createDatabase()

    def createDatabase(self):
        self.db.execute(LOGGING_INITIALIZATION_QUERY)
        self.db.commit()
    
    def emit(self, record):
        self.db.execute(f"INSERT INTO logs (source, time, lvl, lvl_name, msg, name, logger, lineno) VALUES ({self.name}, {time.time()}, {record.levelno}, {record.levelname}, {record.msg}, {record.name}, {record.lineno})")
        self.db.commit()