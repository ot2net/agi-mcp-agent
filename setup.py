"""Setup script for the AGI-MCP-Agent package.

This file is kept for backward compatibility with traditional setuptools-based installations.
For new installations, we recommend using Poetry (pyproject.toml).
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements directly for setuptools compatibility
# These should match the dependencies in pyproject.toml
requirements = [
    "fastapi>=0.104.0",
    "uvicorn>=0.23.2",
    "pydantic>=2.4.2",
    "sqlalchemy>=2.0.22",
    "langchain>=0.0.335",
    "numpy>=1.24.3",
    "python-dotenv>=1.0.0",
    "openai>=1.2.4",
    "tiktoken>=0.5.1",
    "requests>=2.31.0",
]

setup(
    name="agi-mcp-agent",
    version="0.1.0",
    author="OT2.net",
    author_email="info@ot2.net",
    description="An intelligent agent framework based on Master Control Program architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ot2net/agi-mcp-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "agi-mcp-agent-api=agi_mcp_agent.api.server:start_server",
        ],
    },
)