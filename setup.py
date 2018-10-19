import sys
import os
from setuptools import setup

"""
Use pandoc to convert README.md to README.rst before uploading

$ pandoc README.md -o README.rst
"""


if "publish" in sys.argv:
    os.system("python setup.py sdist upload")
    os.system("python setup.py bdist_wheel upload")
    sys.exit()


setup(
    name="piprot",
    version="0.10.0a",
    author="Brenton Cleeland, Marcin Paliwoda",
    author_email="paliwoda.marcin@zoho.com",
    packages=["piprot", "piprot.models", "piprot.utils"],
    url="http://github.com/mpaliwoda/piprot",
    license="MIT License",
    description="How rotten are your requirements?",
    long_description="",
    entry_points={"console_scripts": ["piprot = piprot.entrypoint:entrypoint"]},
    install_requires=["aiohttp", "cchardet", "aiodns"],
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3.7",
    ],
)
