class StreamCommentsDB:
    @staticmethod
    def initialize_table(connection):
        """Create the necessary tables if they don't already exist."""
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

    @staticmethod
    def add_comment(connection, stream_identifier, username, comment):
        """Add a new comment to the database."""
        cursor = connection.cursor()
        cursor.execute("INSERT INTO stream_comments (stream_identifier, username, comment) VALUES (?, ?, ?)", (stream_identifier, username, comment))
        connection.commit()

    @staticmethod
    def query_comments(connection, stream_identifier):
        """Retrieve all comments for a given stream identifier that have not been marked as read."""
        cursor = connection.cursor()
        cursor.execute("SELECT id, username, comment FROM stream_comments WHERE stream_identifier = ? AND read = False", (stream_identifier,))
        return cursor.fetchall()

    @staticmethod
    def mark_comments_as_read(connection, comment_ids):
        """Mark the specified comments as read."""
        cursor = connection.cursor()
        cursor.execute("UPDATE stream_comments SET read = True WHERE id IN ({})".format(','.join('?' * len(comment_ids))), comment_ids)
        connection.commit()

    @staticmethod
    def delete_all_comments(connection):
        """Delete all comments from the database."""
        cursor = connection.cursor()
        cursor.execute("DELETE FROM stream_comments")
        connection.commit()

    @staticmethod
    def save_stream_cursor(connection, stream_identifier, stream_cursor):
        """Save the last seen cursor for a given stream identifier."""
        if stream_cursor is None:
            return
        cursor = connection.cursor()
        cursor.execute("INSERT OR REPLACE INTO stream_cursor (stream_identifier, cursor) VALUES (?, ?)", (stream_identifier, stream_cursor))
        connection.commit()

    @staticmethod
    def get_stream_cursor(connection, stream_identifier):
        """Retrieve the last seen cursor for a given stream identifier."""
        cursor = connection.cursor()
        cursor.execute("SELECT cursor FROM stream_cursor WHERE stream_identifier = ?", (stream_identifier,))
        result = cursor.fetchone()
        if result is not None:
            return result[0]
        return None