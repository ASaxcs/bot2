from setuptools import setup, find_packages

setup(
    name="lacia-ai",
    version="1.0.0",
    description="Complex AI system with personality, memory, and emotional intelligence (GGUF)",
    packages=find_packages(),
    install_requires=[
        "llama-cpp-python>=0.2.20",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "gradio>=4.0.0",
        "pydantic>=2.0.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "python-multipart>=0.0.6",
        "requests>=2.31.0",
        "aiofiles>=23.0.0"
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "lacia-ai=main:main",
        ],
    },
)
