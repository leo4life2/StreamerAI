from openpyxl import load_workbook

class ExcelWorkbook:
    """Abstracts fetching product information from a custom idsg excel format"""

    def __init__(self, worksheet_path):
        self.worksheet_path = worksheet_path
        self.workbook = load_workbook(filename=worksheet_path)

    def worksheets(self):
        return self.workbook.worksheets
    
    def worksheet_for_index(self, index):
        return self.workbook.worksheets[index]
    
    def get_all_product_names_and_descriptions(self):
        names_and_descriptions = []
        for worksheet in self.worksheets():
            name = self.get_product_name(worksheet)
            description = self.get_product_description(worksheet)
            if description and name:
                names_and_descriptions.append((name, description))
        return names_and_descriptions
    
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
    
