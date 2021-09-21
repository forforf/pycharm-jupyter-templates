from setuptools import setup

setup(
    name='nbtplt',
    version='1.0',
    description='Use Pycharm IPython Notebooks to create templates',
    author='forforf',
    author_email='dmarti21@gmail.com',
    packages=['nbtplt'],  # same as name
    install_requires=['nbformat'],  # external packages as dependencies
)
