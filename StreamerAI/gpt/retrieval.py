from langchain.vectorstores import Pinecone
import numpy as np
from StreamerAI.database.database import Product
from langchain.embeddings.openai import OpenAIEmbeddings

class SimpleRetrieval:
    """asdf"""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings()

    def _cosine_similarity(self, a, b):
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)

    def _top_k_products_with_embedding(self, message, k=10):
        result = self.embeddings.embed_query(message)
        message_embedding = np.array(result)

        products = Product.select()
        product_embeddings = [np.frombuffer(p.description_embedding) for p in products]

        # construct np arrays
        message_embedding = np.array(message_embedding).reshape(1, -1)
        product_embeddings = np.array(product_embeddings)

        # compute cosine similarities
        similarities = np.array([self._cosine_similarity(message_embedding, product_embedding) for product_embedding in product_embeddings])

        similarities = similarities.flatten()
        for index, product in enumerate(products):
            product._cached_similarity_score = similarities[index]

        # get top k indices
        top_k_indices = np.argsort(similarities)[::-1][:k]

        return [products[i] for i in top_k_indices]

    def retrieve_top_product_names_with_embedding(self, message, k=10):
        return [p.name for p in self._top_k_products_with_embedding(message, k)]
    
    def add_embedding(self, product_name, product_description):
        pass
    
    def retrieve_with_embedding(self, message):
        products = self._top_k_products_with_embedding(message, 1)
        if len(products) > 0:
            top_product = products[0]
            return top_product.description, top_product.name, top_product._cached_similarity_score
        return '', '', 0

class Retrieval:
    """A class representing a collection of functions for processing user queries and retrieving product information."""

    def __init__(self, pinecone_index, embeddings, text_key):
        self.vectorstore = Pinecone(pinecone_index, embeddings.embed_query, text_key)
    
    def retrieve_top_product_names_with_embedding(self, message, k=10):
        """
        """
        documents = self.vectorstore.similarity_search(message, k)
        if len(documents) == 0:
            return []
        
        results = []
        for document in documents:
            product_name = str(document.metadata["product_name"])

            product = Product.select().where(Product.name == product_name).get()
            if product:
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
            product = Product.select().where(Product.name == product_name).get()
            if product and product.description is not None:
                return product.description, product.name, score
        return '', '', 0

