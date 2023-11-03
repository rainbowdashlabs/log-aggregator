import logging
from datetime import datetime, UTC
from functools import wraps
from threading import Thread
from time import sleep

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError, NetworkTimeout, OperationFailure

from configuration import config

mongo = config().mongo

INDEX_FIELD = config().indices.index_field

log = logging.getLogger(__name__)

_client: MongoClient | None = None
_db: Database | None = None
_logs: Collection | None = None
_meta: Collection | None = None


def connect():
    global _client, _db, _logs, _meta
    log.info('Connecting to mongo db')
    _client = MongoClient(mongo.uri())
    _db = _client.get_database(mongo.database)
    _logs = _db.get_collection('logs')
    _meta = _db.get_collection('meta')


def setup():
    connect()
    _logs.create_index([INDEX_FIELD, ('_timestamp', pymongo.DESCENDING)], background=True, sparse=True)
    _logs.create_index([('_timestamp', pymongo.DESCENDING)])

    Thread(target=cleanup).start()


def collection():
    return _logs


def mongo_reconnect(retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(1, retries):
                try:
                    return func(*args, **kwargs)
                except (ServerSelectionTimeoutError, NetworkTimeout, OperationFailure) as e:
                    if i < retries:
                        log.warning(f"Connection error ({e}), retrying...")
                        connect()
                        continue
                    else:
                        log.error("Failed to connect after multiple attempts")
                break

        return wrapper

    return decorator


@mongo_reconnect()
def add_log(record: dict):
    record['_timestamp'] = datetime.now(UTC)
    _logs.insert_one(record)


def cleanup():
    while True:
        log.debug('Performing cleanup')
        _cleanup_known()
        _cleanup_unkown()
        sleep(60*60)


@mongo_reconnect()
def _cleanup_known():
    for index, conf in config().indices.indices.items():
        if not conf.retention.active:
            continue
        after = conf.retention.timestamp()
        _logs.delete_many({INDEX_FIELD: index, "_timestamp": {"$lt": after}})


@mongo_reconnect()
def _cleanup_unkown():
    after = config().retention.timestamp()
    condition = {
        "_timestamp": {"$lt": after},
        "$or": [
            {INDEX_FIELD: {"$exists": False}},
            {INDEX_FIELD: {"$nin": list(config().indices.indices.keys())}}
        ]
    }
    _logs.delete_many(condition)


setup()
