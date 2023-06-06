import logging
import time

from StreamerAI.gpt.chains import Chains
from StreamerAI.database.database import Product

logger = logging.getLogger("StreamChatBaseHandler")

class StreamChatBaseHandler():

    @staticmethod
    def get_comment_response(username: str, message: str):
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
        
        return response

    async def on_heartbeat(self, message: str):
        raise NotImplementedError()

    async def on_comment(self, message: str):
        raise NotImplementedError()

    async def on_gift(self, message: str):
        raise NotImplementedError()

    async def on_purchase(self, message: str):
        raise NotImplementedError()