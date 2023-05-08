from langchain.vectorstores import Pinecone
from openpyxl import load_workbook
from pathlib import Path
import sqlite3
from StreamerAI.settings import DATABASE_PATH
from StreamerAI.database import StreamCommentsDB
import os


class Retrieval:
    """A class representing a collection of functions for processing user queries and retrieving product information."""

    def __init__(self, pinecone_index, embeddings, text_key):
        self.vectorstore = Pinecone(pinecone_index, embeddings.embed_query, text_key)
        self.connection = sqlite3.connect(DATABASE_PATH)
    
    def retrieve_top_product_names_with_embedding(self, message, k=10):
        """
        """
        documents = self.vectorstore.similarity_search(message, k)
        if len(documents) == 0:
            return []
        
        results = []
        for document in documents:
            product_name = str(document.metadata["product_name"])
            description = StreamCommentsDB.product_description_for_name(self.connection, product_name)
            if len(description) > 0:
                results.append(product_name)

        return results
    
    def add_embedding(self, product_name, product_description):
        """
        """
        metadata = {
            "product_name": product_name,
        }
        self.vectorstore.add_texts([product_description], [metadata])

    def retrieve_with_embedding(self, message):
        """
        """
        res = self.vectorstore.similarity_search_with_score(message, 1)[0]
        if len(res) > 0:
            document, score = res[0], res[1]
            product_name = str(document.metadata["product_name"])
            description = StreamCommentsDB.product_description_for_name(self.connection, product_name)
            if len(description) > 0:
                return description[0], product_name, score
        return '', '', 0

