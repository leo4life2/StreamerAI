import argparse
import logging
import numpy
import os
from StreamerAI.database.database import Assistant, Product, Asset
from StreamerAI.gpt.retrieval import Retrieval
from langchain.embeddings.openai import OpenAIEmbeddings
from StreamerAI.settings import BOOTSTRAP_DATA_DIRECTORY, PINECONE_INDEX, PINECONE_TEXT_KEY

class DatasetBootstrapper:
    """Initializes the StreamerAI database with a set of default assistant profiles, as wel as (optionally) additional data"""

    def __init__(self, data_directory):
        self.data_directory = data_directory
        self.embeddings = OpenAIEmbeddings()
        self.retrieval = Retrieval(PINECONE_INDEX, self.embeddings, PINECONE_TEXT_KEY)

    def bootstrap_assistants(self):
        for filename in os.listdir(os.path.join(self.data_directory, "assistants")):
            filepath = os.path.join(self.data_directory, "assistants", filename)
            f = open(filepath, "r")
            
            split_tup = os.path.splitext(filename)
            name = split_tup[0]
            ext = split_tup[1]
            prompt = f.read()

            existing_assistants = Assistant.select().where(Assistant.name == name).count()
            if existing_assistants == 0:
                assistant = Assistant.create(name=name, prompt=prompt)
                logging.info(f"Bootstrapped assistant {assistant}")
            else:
                logging.info(f"Assistant {name} already exists, skipping...")

    def bootstrap_products(self):
        for directory in os.listdir(os.path.join(self.data_directory, "products")):
            logging.info(f"dir: {directory}")
            if directory == ".DS_Store":
                continue

            name_path = os.path.join(self.data_directory, "products", directory, "name.txt")
            description_path = os.path.join(self.data_directory, "products", directory, "description.txt")
            script_path = os.path.join(self.data_directory, "products", directory, "script.txt")

            name_file = open(name_path, 'r')
            description_file = open(description_path, 'r')
            script_file = open(script_path, 'r')

            product_name = name_file.read()
            product_description = description_file.read()
            product_script = script_file.read()

            product_description_embedding = self.embeddings.embed_query(product_description)
            if not len(product_description_embedding) > 0:
                logging.info(f"Could not retrieve embedding for {product_name}, skipping...")
                continue
            product_description_embedding = numpy.array(product_description_embedding)

            existing_product_ct = Product.select().where(Product.name == product_name).count()
            if existing_product_ct != 0:
                logging.info(f"Product {product_name} already exists, skipping...")
                continue
                
            product = Product.create(name=product_name, description=product_description, description_embedding=product_description_embedding, script=product_script)
            self.retrieval.add_embedding(product_name, product_description)
            logging.info(f"Added product {product.name}")

            for asset_filename in os.listdir(os.path.join(self.data_directory, "products", directory, "assets")):
                asset_path = os.path.join(self.data_directory, "products", directory, "assets", asset_filename)
                asset_file = open(asset_path, "rb")

                split_tup = os.path.splitext(asset_filename)
                
                asset_name = split_tup[0]
                asset_ext = split_tup[1]
                asset_blob = asset_file.read()

                existing_asset_ct = Asset.select().where(Asset.name == asset_name).count()
                if existing_asset_ct != 0:
                    logging.info(f"Asset {asset_name} already exists, skipping...")
                    continue
                
                asset = Asset.create(name=asset_name, extension=asset_ext, product=product, asset=asset_blob)
                logging.info(f"Added asset {asset} ")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--assistants', action='store_true', help='Bootstrap assistants')
    parser.add_argument('--products', action='store_true', help='Bootstrap products')

    args = parser.parse_args()

    bootstrapper = DatasetBootstrapper(BOOTSTRAP_DATA_DIRECTORY)

    if (args.assistants):
        bootstrapper.bootstrap_assistants()
    
    if (args.products):
        bootstrapper.bootstrap_products()
