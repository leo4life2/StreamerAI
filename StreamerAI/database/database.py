class StreamCommentsDB:
    @staticmethod
    def initialize_table(connection):
        """Create the necessary tables if they don't already exist."""
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stream_comments (
                id INTEGER PRIMARY KEY, /* unique id primary key */
                stream_identifier TEXT NOT NULL, /* unique identifier that represents the stream, likely the streaming platform's channel id */
                username TEXT NOT NULL, /* username of the commenter */
                comment TEXT NOT NULL, /* text of the comment */
                read INTEGER NOT NULL DEFAULT FALSE /* whether the comment has been processed by the assistant or not */
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS stream_cursor (
                stream_identifier TEXT PRIMARY KEY, /* unique identifier that represents the stream, likely the streaming platform's channel id */
                cursor TEXT NOT NULL /* the stream comment cursor */
            );
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                name TEXT PRIMARY KEY, /* name of the product */
                description TEXT NOT NULL /* description of the product, FAQs, etc. will be directly injected into the prompt */
            );
            """
            # we can consider separating description into multiple columns - get this working for now
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS assistants (
                name TEXT PRIMARY KEY, /* name of the assistant profile */
                prompt TEXT NOT NULL /* a description/command of how the assistant should behave. this will be directly injected into the prompt */
            );
            """
        )
        connection.commit()

    @staticmethod
    def add_product(connection, name, description):
        """Add a new product"""
        cursor = connection.cursor()
        cursor.execute("INSERT INTO products (name, description) VALUES (?, ?)", (name, description))
        connection.commit()

    @staticmethod
    def product_description_for_name(connection, name):
        """asdf"""
        cursor = connection.cursor()
        cursor.execute("SELECT description FROM products WHERE name = ?", (name,))
        return cursor.fetchall()
    
    @staticmethod
    def query_all_products(connection):
        """Returns all registered products"""
        cursor = connection.cursor()
        cursor.execute("SELECT name, description FROM products")
        return cursor.fetchall()

    @staticmethod
    def remove_product(connection, name):
        """Remove the product with the specified name"""
        cursor = connection.cursor()
        cursor.execute("DELETE FROM products WHERE name = ?", (name,))
        cursor.commit()

    @staticmethod
    def add_assistant(connection, name, prompt):
        """Add a new assistant profile"""
        cursor = connection.cursor()
        cursor.execute("INSERT INTO assistants (name, prompt) VALUES (?, ?)", (name, prompt))
        connection.commit()

    @staticmethod
    def get_prompt_for_assistant(connection, name):
        """Given an assistant name, fetches the prompt that should be used"""
        cursor = connection.cursor()
        cursor.execute("SELECT prompt FROM assistants WHERE name = ?", (name,))
        return cursor.fetchall()

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