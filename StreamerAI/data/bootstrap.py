import argparse
import sqlite3
import logging
from StreamerAI.settings import DATABASE_PATH, BOOTSTRAP_EXCEL_FILE_PATH
from StreamerAI.database import StreamCommentsDB
from StreamerAI.data.excel import ExcelWorkbook

class DatasetBootstrapper:
    """Initializes the StreamerAI database with a set of default assistant profiles, as wel as (optionally) additional data"""

    def __init__(self, connection, product_workbook):
        self.connection = connection
        StreamCommentsDB.initialize_table(self.connection)
        self.product_workbook = product_workbook

    def bootstrap_assistants(self):
        default_prompt = """
        You are an AI-powered sales assistant who is well-versed in the features and benefits of the product you are selling.
        Your goal is to help customers understand how the product can solve their problems and meet their needs, and to convince them that it is the best solution available.
        With your expertise and knowledge, you can provide personalized recommendations and address any concerns or objections that customers may have, ultimately closing the deal and generating sales for the company.

        Use the information in "Product Information" to answer a user's question about a specific product. If a user asks about available products, use the information in "Other Available Products".
        If you are given a question unrelated to health or the product or list of other available products, you should respond saying that you are only capable of answering questions about available products.
        However, you are also a health and nutrition expert, so you can answer questions related to these fields. Try to answer your questions in Chinese as much as possible.
        If you are unsure about what product the user is referring to, or if the product information given doesn't seem to match the user's question, ask the user a follow up question to clarify.

        You must respond to all questions in Chinese, even if the question is in a different language
        """
        default_assistant_name = "default"
        existing_prompts = StreamCommentsDB.get_prompt_for_assistant(self.connection, default_assistant_name)
        if len(existing_prompts) == 0:
            StreamCommentsDB.add_assistant(self.connection, default_assistant_name, default_prompt)
            logging.info("Bootstrapped default assistant")
        else:
            logging.info("Default assistant already exists, skipping...")

    def bootstrap_products(self):
        for (name, description) in self.product_workbook.get_all_product_names_and_descriptions():
            existing_description = StreamCommentsDB.product_description_for_name(self.connection, name)
            if len(existing_description) == 0:
                StreamCommentsDB.add_product(self.connection, name, description)
                logging.info(f"Bootstrapped product with name: {name}")
            else:
                logging.info(f"Product with name {name} already exists, skipping...")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--assistants', action='store_true', help='Bootstrap assistants')
    parser.add_argument('--products', action='store_true', help='Bootstrap products')

    args = parser.parse_args()

    connection = sqlite3.connect(DATABASE_PATH)
    product_workbook = ExcelWorkbook(BOOTSTRAP_EXCEL_FILE_PATH)
    bootstrapper = DatasetBootstrapper(connection, product_workbook)

    if (args.assistants):
        bootstrapper.bootstrap_assistants()
    
    if (args.products):
        bootstrapper.bootstrap_products()
