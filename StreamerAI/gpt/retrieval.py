from langchain.vectorstores import Pinecone
from openpyxl import load_workbook
from pathlib import Path

import os


class Retrieval:
    """A class representing a collection of functions for processing user queries and retrieving product information."""

    def __init__(self, pinecone_index, embeddings, text_key):
        self.vectorstore = Pinecone(pinecone_index, embeddings.embed_query, text_key)

    def get_product_description(self, worksheet):
        """Retrieve the description of a product from the given worksheet.

        Args:
            worksheet: the worksheet containing the product information

        Returns:
            str: the description of the product
        """
        label_value_tuples = []
        for row_num in range(1, 1000):
            label_cell = worksheet["A" + str(row_num)]
            value_cell = worksheet["B" + str(row_num)]
            if label_cell.value is None or value_cell.value is None:
                break
            label_value_tuple = str(label_cell.value) + ": " + str(value_cell.value)
            label_value_tuples.append(label_value_tuple)

        # join the tuples together w/ newlines to form text
        text = "\n".join(label_value_tuples)
        return text

    def get_product_name(self, worksheet):
        """Retrieve the name of a product from the given worksheet.

        Args:
            worksheet: the worksheet containing the product information

        Returns:
            str: the name of the product
        """
        value_cell = worksheet["B1"]
        if value_cell.value is None:
            return ""
        name = str(value_cell.value)
        return name.replace("\n", "")

    def get_worksheet_with_index(self, index):
        """Retrieve the worksheet containing the product information for the given index.

        Args:
            index: the index of the worksheet to retrieve

        Returns:
            worksheet: the worksheet containing the product information
        """
        # Get the current working directory
        cwd = Path.cwd()

        # Set the path to the data.xlsx file
        data_xlsx_path = os.path.join(cwd, "data", "data.xlsx")

        # Load the workbook and return the specified worksheet
        workbook = load_workbook(filename=data_xlsx_path)
        return workbook.worksheets[index]

    def get_product_description_with_index(self, index):
        """Retrieve the description of the product with the given index.

        Args:
            index: the index of the product to retrieve

        Returns:
            str: the description of the product
        """
        worksheet = self.get_worksheet_with_index(index)
        desc = self.get_product_description(worksheet)
        return desc

    def retrieve_top_product_names_with_embedding(self, message, k=10):
        """Retrieve a list of the top k product names based on the given query.

        Args:
            message (str): the user's query
            k (int): the number of product names to retrieve

        Returns:
            list: a list of the top k product names
        """
        documents = self.vectorstore.similarity_search(message, k)
        if len(documents) == 0:
            return []

        results = []
        for document in documents:
            index = document.metadata.get('index')
            if index:
                index = int(index)
                worksheet = self.get_worksheet_with_index(index)
                name = self.get_product_name(worksheet)
                results.append(name)

        return results
    
    def retrieve_with_embedding(self, message):
        """Retrieve the most relevant product description for the given query.

        Args:
            message (str): the user's query

        Returns:
            str: the product description
            int: the index of the product
            float: the similarity score
        """
        # retrieve top document
        res = self.vectorstore.similarity_search_with_score(message, 1)[0]
        if len(res) > 0:
            document, score = res[0], res[1]
            index = int(document.metadata['index'])
            worksheet = self.get_worksheet_with_index(index)
            desc = self.get_product_description(worksheet)
            return desc, int(index), score
        return '', 0, 0
