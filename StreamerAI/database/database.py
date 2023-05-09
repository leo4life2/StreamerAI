from StreamerAI.settings import DATABASE_PATH
from peewee import SqliteDatabase, Model, CharField, BlobField, ForeignKeyField, TextField, BooleanField

StreamCommentsDB = SqliteDatabase(DATABASE_PATH, pragmas={
    'journal_mode': 'wal',
    'foreign_keys': 1,  # Enforce foreign-key constraints
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
    read = BooleanField()

class Assistant(BaseModel):
    name = CharField(primary_key=True, unique=True)
    prompt = TextField()

class Product(BaseModel):
    name = CharField(primary_key=True, unique=True)
    description = TextField()
    description_embedding = BlobField()
    script = TextField()

class Asset(BaseModel):
    name = CharField(primary_key=True, unique=True)
    extension = CharField()
    product = ForeignKeyField(Product, backref="assets")
    asset = BlobField()

with StreamCommentsDB:
    StreamCommentsDB.create_tables([Stream, Comment, Assistant, Product, Asset])