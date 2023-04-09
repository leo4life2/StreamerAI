# TODO: make this work in a generic way
def script_for_product_index(product_index):
    filename = "./src/gpt/product_scripts/{}.txt".format(product_index)
    print("using filename: {}".format(filename))
    file = open(filename, "r")
    data = file.read()
    return [paragraph for paragraph in data.split("\n") if paragraph != '']
