"""
Setup configuration for AI Documentation Generator
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-doc-generator",
    version="1.0.0",
    author="Muhammad Haseeb",
    author_email="muhamadhaseeb2001@gmail.com",
    description="AI-powered documentation generator for Python projects using OpenAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haseebrj17/ai-doc-generator",
    project_urls={
        "Bug Tracker": "https://github.com/haseebrj17/ai-doc-generator/issues",
        "Documentation": "https://github.com/haseebrj17/ai-doc-generator/wiki",
        "Source Code": "https://github.com/haseebrj17/ai-doc-generator",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "tqdm>=4.65.0",
        "pathlib>=1.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-doc-gen=ai_doc_generator.cli:main",
            "aidocgen=ai_doc_generator.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)