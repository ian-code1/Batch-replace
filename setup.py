"""
Setup configuration for the batch search-and-replace tool.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="batch-replace-tool",
    version="1.0.0",
    author="Your Department",
    description="A safe, configurable batch search-and-replace tool for text files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourdepartment/batch-replace-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "chardet>=5.0.0",
    ],
    extras_require={
        'yaml': ['pyyaml>=6.0'],
        'colors': ['colorama>=0.4.6', 'rich>=13.0.0'],
        'dev': ['pytest>=7.0.0', 'pytest-cov>=4.0.0'],
    },
    entry_points={
        "console_scripts": [
            "batch-replace=batch_replace.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)