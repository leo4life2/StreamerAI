import os

def fetch_scripts():
    # Get the absolute path of the directory containing the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    scripts = []

    for filename in sorted(os.listdir(dir_path + '/product_scripts/')):
        file = open(dir_path + '/product_scripts/' + filename, "r", encoding="utf-8")
        data = file.read()
        paragraphs = [paragraph for paragraph in data.split("\n") if paragraph != '']
        scripts.append(paragraphs)
    
    return scripts
