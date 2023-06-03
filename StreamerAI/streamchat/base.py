import logging
import time

from StreamerAI.gpt.chains import Chains
from StreamerAI.database.database import Product

logger = logging.getLogger("StreamChatBaseHandler")

class StreamChatBaseHandler():

    def __init__(self):
        self.max_comments_per_window = 3
        self.window_size_in_seconds = 30
        self.window_start_time = time.time()
        self.window_comment_count = 0
        self.total_received_comment_count = 0
        self.total_passed_comment_count = 0

    def meets_rate_limit(self):
        current_time = time.time()
        time_since_window_start = current_time - self.window_start_time

        if time_since_window_start > self.window_size_in_seconds:
            self.window_start_time = current_time
            self.window_comment_count = 0

        if self.window_comment_count < self.max_comments_per_window:
            self.window_comment_count += 1
            self.total_passed_comment_count += 1
            self.total_received_comment_count += 1
            logger.info(
                f"comment passed window limit starting at {self.window_start_time} with current count {self.window_comment_count}\n"
                f"total received comments: {self.total_received_comment_count} total passed comments: {self.total_passed_comment_count} "
            )
            return True
        else:
            self.total_received_comment_count += 1
            logger.info(
                f"comment failed window limit starting at {self.window_start_time} with current count {self.window_comment_count}\n"
                f"total received comments: {self.total_received_comment_count} total passed comments: {self.total_passed_comment_count} "
            )
            return False

    def get_comment_response(self, username: str, message: str):
        start = time.time()

        current_product = Product.select().where(Product.current == True).first()
        product_description = current_product.description if current_product != None else None
        logger.info(f"found current product: {current_product}")

        chain = Chains.create_chain()

        product_context, name = Chains.get_product_context(message, product_description)
        logger.info(f"using product: {name}")

        other_products = Chains.get_product_list_text(message)
        logger.debug(f"using other products:\n{other_products}")

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

        end = time.time()
        time_taken = end - start
        logger.info(f"time taken to process comment: {time_taken} seconds")


    async def on_heartbeat(self, message: str):
        raise NotImplementedError()

    async def on_comment(self, message: str):
        raise NotImplementedError()

    async def on_gift(self, message: str):
        raise NotImplementedError()

    async def on_purchase(self, message: str):
        raise NotImplementedError()