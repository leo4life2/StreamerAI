import argparse
import sqlite3
import logging
import os
from StreamerAI.settings import DATABASE_PATH, BOOTSTRAP_DATA_DIRECTORY
from StreamerAI.database import StreamCommentsDB
from StreamerAI.gpt.retrieval import Retrieval
from langchain.embeddings.openai import OpenAIEmbeddings
from StreamerAI.settings import PINECONE_INDEX, PINECONE_TEXT_KEY

class DatasetBootstrapper:
    """Initializes the StreamerAI database with a set of default assistant profiles, as wel as (optionally) additional data"""

    def __init__(self, connection, data_directory):
        self.connection = connection
        StreamCommentsDB.initialize_table(self.connection)
        self.data_directory = data_directory
        self.retrieval = Retrieval(PINECONE_INDEX, OpenAIEmbeddings(), PINECONE_TEXT_KEY)

    def bootstrap_assistants(self):
        for filename in os.listdir(os.path.join(self.data_directory, "assistants")):
            filepath = os.path.join(self.data_directory, "assistants", filename)
            f = open(filepath, "r")
            
            name = filename
            prompt = f.read()

            existing_prompts = StreamCommentsDB.get_prompt_for_assistant(self.connection, name)
            if len(existing_prompts) == 0:
                StreamCommentsDB.add_assistant(self.connection, name, prompt)
                logging.info("Bootstrapped default assistant")
            else:
                logging.info("Default assistant already exists, skipping...")

    def bootstrap_products(self):
        for directory in os.listdir(os.path.join(self.data_directory, "products")):
            logging.info(f"dir: {directory}")

            name_path = os.path.join(self.data_directory, "products", directory, "name.txt")
            description_path = os.path.join(self.data_directory, "products", directory, "description.txt")
            script_path = os.path.join(self.data_directory, "products", directory, "script.txt")

            name_file = open(name_path, 'r')
            description_file = open(description_path, 'r')
            script_file = open(script_path, 'r')

            product_name = name_file.read()
            product_description = description_file.read()
            product_script = script_file.read()

            existing_product = StreamCommentsDB.product_description_for_name(self.connection, product_name)
            if len(existing_product) != 0:
                logging.info(f"Product {product_name} already exists, skipping...")
                continue
                
            StreamCommentsDB.add_product(self.connection, product_name, product_description, product_script)
            self.retrieval.add_embedding(product_name, product_description)
            logging.info(f"Added product {product_name}")

            for asset_filename in os.listdir(os.path.join(self.data_directory, "products", directory, "assets")):
                asset_path = os.path.join(self.data_directory, "products", directory, "assets", asset_filename)
                asset_file = open(asset_path, "rb")

                split_tup = os.path.splitext(asset_filename)
                
                asset_name = split_tup[0]
                asset_ext = split_tup[1]
                asset_blob = asset_file.read()

                existing_asset = StreamCommentsDB.get_asset(self.connection, product_name, asset_name)
                if len(existing_asset) != 0:
                    logging.info(f"Asset {asset_name} already exists, skipping...")
                    continue

                StreamCommentsDB.add_asset(self.connection, product_name, asset_name, asset_ext, asset_blob)
                logging.info(f"Added asset {asset_name} ")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--assistants', action='store_true', help='Bootstrap assistants')
    parser.add_argument('--products', action='store_true', help='Bootstrap products')

    args = parser.parse_args()

    connection = sqlite3.connect(DATABASE_PATH)
    bootstrapper = DatasetBootstrapper(connection, BOOTSTRAP_DATA_DIRECTORY)

    if (args.assistants):
        bootstrapper.bootstrap_assistants()
    
    if (args.products):
        bootstrapper.bootstrap_products()
