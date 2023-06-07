import logging
import time
import uuid

from StreamerAI.gpt.chains import Chains
from StreamerAI.database.database import Comment, Product, Stream
from StreamerAI.streamchat.ratelimiter import RateLimiter

logger = logging.getLogger("StreamChatHandler")


class StreamChatHandler:
    """
    Class for handling chat in a stream
    """

    def __init__(self, room_id: str, platform: str):
        """
        Initialize a new StreamChatHandler.

        Args:
            room_id: The unique identifier for a chat room.
            platform: The platform of the stream.
        """
        self.room_id = room_id
        self.platform = platform
        self.rate_limiter = RateLimiter(2, 30) # 2 comments every 30 seconds

    @staticmethod
    def get_comment_response(username: str, message: str):
        """
        Get the bot's response to a user comment.

        Args:
            username: The username of the user who made the comment.
            message: The comment message.

        Returns:
            The bot's response to the comment.
        """
        return None
        # Time the comment processing
        start = time.time()
        
        # Get the current product
        current_product = Product.select().where(Product.current == True).first()
        product_description = current_product.description if current_product else None
        logger.info(f"Found current product: {current_product}")

        # Create a new conversation chain
        chain = Chains.create_chain()

        # Get the context related to the product from the message
        product_context, name = Chains.get_product_context(message, product_description)
        logger.info(f"Using product: {name}")

        # Get a text list of other available products
        other_products = Chains.get_product_list_text(message)
        logger.debug(f"Using other products:\n{other_products}")

        # Predict the bot's response
        response = chain.predict(
            human_input=message,
            product_context=product_context,
            other_available_products=other_products,
            audience_name=username
        )
        logger.info(
            f"Chat Details:\n"
            f"Message: {message}\n"
            f"Response: {response}\n"
        )

        logger.info(f"Time taken to process comment: {time.time() - start} seconds")

        return response

    def on_comment(self, username: str, text: str):
        """
        Handle a new comment in the chat.

        Args:
            username: The username of the user who made the comment.
            text: The comment message.
        """
        # Log the incoming comment
        logger.info(f"[{self.platform}] comment: {username}: {text}")

        if not self.rate_limiter.meets_limit():
            return

        # Get the stream for the current room
        stream = Stream.select().where(Stream.identifier == self.room_id).get()
        past_cursor = stream.cursor
        logger.info(f"[{self.platform}] fetching existing stream cursor for room_id: {self.room_id}, existing cursor: {past_cursor}")

        # Get the bot's response to the comment
        response = self.get_comment_response(username, text)
        if not response:
            logger.info("Could not generate response, skipping comment")
            return

        # Add the comment and the response to the database
        Comment.create(stream=stream, username=username, comment=text, read=False, reply=response)
        logger.info(f"[{self.platform}] adding new comment for room_id: {self.room_id}")

        # Update the stream's cursor
        cursor = str(uuid.uuid4())
        stream.cursor = cursor
        stream.save()
        logger.info(f"[{self.platform}] saving new stream cursor for room_id: {self.room_id}, new cursor: {cursor}")
        
    def on_gift(self, username: str, gift_description: str):
        """
        Handle a new gift in the chat.
        
        Args:
            username: The username of the user who sent the gift.
            gift_description: The description of the gift.
        """
        logger.info(f"[{self.platform}] gift: {username}: {gift_description}")
        
    def on_join(self, username: str):
        """
        Handle a new user joining the chat.

        Args:
            username: The username of the user who joined.
        """
        logger.info(f"[{self.platform}] joined the stream: {username}")
        
    def on_follow(self, username: str):
        """
        Handle a new user following the stream.

        Args:
            username: The username of the user who followed.
        """
        logger.info(f"[{self.platform}] followed the streamer: {username}")
        
    def on_heartbeat(self, message: str):
        """
        Handle a new heartbeat message.

        Args:
            message: The heartbeat message.
        """
        logger.info(f"[{self.platform}] heartbeat: {message}")