from setuptools import setup, find_packages

setup(
    name="melodi",
    version="1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "melodi = melodi.cli:cli",
        ],
    },
)
