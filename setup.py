from setuptools import setup, find_packages

def read_requirements():
    with open('requirements.txt') as req:
        return req.read().splitlines()

setup(
    name='apis',
    version='0.1',
    packages=find_packages(),
    install_requires=read_requirements(),
)