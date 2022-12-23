
from setuptools import setup


with open("README.md", encoding='utf-8') as f:
    long_description = f.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="Balance_Bot",
    version="0.5",
    packages=['configs', 'logs', 'tests', 'balance_bot', 'tests.module', 'tests.function'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=required,
)
