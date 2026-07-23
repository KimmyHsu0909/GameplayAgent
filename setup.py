from setuptools import setup, find_packages

setup(
    name="vg-bench",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "pyboy>=2.5.1",
        "pygame>=2.1.0",
        "pillow>=9.0.0",
        "pydantic>=2.0.0",
        "pytest>=7.0.0",
        "tqdm>=4.65.0",
        "rich>=13.0.0",
        "gymnasium>=0.29.0",
    ],
    python_requires=">=3.8",
) 