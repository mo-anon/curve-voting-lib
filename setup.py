from setuptools import setup, find_packages

setup(
    name="curve-voting-lib",
    version="0.1.0",
    description="A Python package to simplify the creation, validation and simulation of Curve DAO votes",
    author="mo",
    author_email="moanonresearch@gmail.com",
    packages=find_packages(),
    install_requires=[
        "titanoboa>=0.2.6",
        "python-dotenv>=1.0.0",
        "hexbytes>=0.3.0",
    ],
    python_requires=">=3.8",
) 