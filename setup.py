# pylint: skip-file
from setuptools import setup
from gja import __version__

with open("README.md", encoding="utf8") as f:
    README = f.read()

setup(
    name="gja",
    version=__version__,
    description="Gauss-Jordan assistant",
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    url="https://github.com/aroberge/gauss-jordan-assistant",
    author="André Roberge",
    author_email="Andre.Roberge@gmail.com",
    py_modules=["gja"],
    python_requires=">=3.8",
    install_requires=["rich"]
)
