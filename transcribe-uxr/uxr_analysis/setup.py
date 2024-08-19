from setuptools import find_packages, setup

setup(
    name="uxr_analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3",
        "pandas",
        "markdown",
        "tabulate",
    ],
    entry_points={
        "console_scripts": [
            "uxr_analysis=src.cli:main",
        ],
    },
)
