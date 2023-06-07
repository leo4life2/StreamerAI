from StreamerAI.settings import DATABASE_PATH
from peewee import SqliteDatabase, Model, CharField, BlobField, ForeignKeyField, TextField, BooleanField
import os
import logging

# Uncomment to include executed SQL queries in the logs
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

StreamCommentsDB = SqliteDatabase(DATABASE_PATH, pragmas={
    'journal_mode': 'wal', # allow readers and writers to co-exist
    'foreign_keys': 1,  # enforce foreign-key constraints
    'ignore_check_constraints': 0, # enforce CHECK constraints
    'synchronous': 2, # checkpoint WAL on every commit, has the side-effect of making sure new data shows up to readers faster
})

class BaseModel(Model):
    class Meta:
        database = StreamCommentsDB

class Stream(BaseModel):
    identifier = CharField(primary_key=True, unique=True)
    cursor = BlobField(null=True)

class Comment(BaseModel):
    stream = ForeignKeyField(Stream, backref="comments")
    username = CharField()
    comment = CharField()
    reply = TextField()
    read = BooleanField()

class Product(BaseModel):
    name = CharField(primary_key=True, unique=True)
    description = TextField()
    description_embedding = BlobField()
    script = TextField()
    current = BooleanField()

class Asset(BaseModel):
    name = CharField(primary_key=True, unique=True)
    product = ForeignKeyField(Product, backref="assets")
    asset = BlobField()

ALL_TABLES = [Stream, Comment, Product, Asset]

def reset_database():
    def _delete_if_exists(path):
        if os.path.exists(path):
            os.remove(path)

    db_path = DATABASE_PATH
    shm_path = db_path + "-shm"
    wal_path = db_path + "-wal"

    _delete_if_exists(db_path)
    _delete_if_exists(shm_path)
    _delete_if_exists(wal_path)

    # need to re-create tables again after
    with StreamCommentsDB:
        StreamCommentsDB.create_tables(ALL_TABLES)


with StreamCommentsDB:
    StreamCommentsDB.create_tables(ALL_TABLES)