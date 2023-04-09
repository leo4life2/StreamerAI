import sqlite3

def initialize_table(connection):
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stream_comments (
            id INTEGER PRIMARY KEY,
            stream_identifier TEXT NOT NULL,
            username TEXT NOT NULL,
            comment TEXT NOT NULL,
            read INTEGER NOT NULL DEFAULT FALSE
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stream_cursor (
            stream_identifier TEXT PRIMARY KEY,
            cursor TEXT NOT NULL
        );
        """
    )
    connection.commit()

def add_comment(connection, stream_identifier, username, comment):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO stream_comments (stream_identifier, username, comment) VALUES (?, ?, ?)", (stream_identifier, username, comment))
    connection.commit()

def query_comments(connection, stream_identifier):
    cursor = connection.cursor()
    cursor.execute("SELECT id, username, comment FROM stream_comments WHERE stream_identifier = ? AND read = False", (stream_identifier,))
    return cursor.fetchall()

def mark_comments_as_read(connection, comment_ids):
    cursor = connection.cursor()
    cursor.execute("UPDATE stream_comments SET read = True WHERE id IN ({})".format(','.join('?' * len(comment_ids))), comment_ids)
    connection.commit()

def delete_all_comments(connection):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM stream_comments")
    connection.commit()

def save_stream_cursor(connection, stream_identifier, stream_cursor):
    if stream_cursor is None:
        return
    cursor = connection.cursor()
    cursor.execute("INSERT OR REPLACE INTO stream_cursor (stream_identifier, cursor) VALUES (?, ?)", (stream_identifier, stream_cursor))
    connection.commit()

def get_stream_cursor(connection, stream_identifier):
    cursor = connection.cursor()
    cursor.execute("SELECT cursor FROM stream_cursor WHERE stream_identifier = ?", (stream_identifier,))
    result = cursor.fetchone()
    if result is not None:
        return result[0]
    return None