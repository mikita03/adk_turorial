from setuptools import setup, find_packages

setup(
    name="google_adk",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "google-generativeai>=0.8.0",
        "mcp-agent>=0.1.0",
    ],
    description="Google Agent Development Kit (ADK) Tutorial",
    author="Devin AI",
    author_email="devin-ai-integration[bot]@users.noreply.github.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
