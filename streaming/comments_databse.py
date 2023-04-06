import sqlite3

def initialize_table(connection):
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stream_comments (
            id INTEGER PRIMARY KEY,
            stream_identifier TEXT NOT NULL,
            username TEXT NOT NULL,
            comment TEXT NOT NULL
        );
        """
    )
    connection.commit()

def add_comment(connection, stream_identifier, username, comment):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO stream_comments (stream_identifier, username, comment) VALUES (?, ?, ?)", (stream_identifier, username, comment))
    connection.commit()

def query_comments(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM stream_comments")
    return cursor.fetchAll()

def delete_all_comments(connection):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM stream_comments")
    connection.commit()
