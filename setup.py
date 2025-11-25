"""
Setup script for RoboCompute SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="robocompute-sdk",
    version="1.0.0",
    author="RoboCompute Team",
    author_email="support@robocompute.io",
    description="Official SDK for RoboCompute decentralized computing platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robocompute/robocompute-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "websocket-client>=1.6.0",
        "solana>=0.30.0",
        "base58>=2.1.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
            "ruff>=0.0.287",
        ],
        "fastapi": [
            "fastapi>=0.104.0",
            "uvicorn>=0.24.0",
        ],
        "flask": [
            "flask>=3.0.0",
        ],
        "ros2": [
            "rclpy>=3.3.0",
        ],
    },
)

