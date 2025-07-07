from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="school-of-prompt",
    version="0.2.0",
    author="Gustavo Pereyra",
    author_email="gpereyra@users.noreply.github.com",
    description="🎸 Rock your prompts! Simple, powerful prompt optimization with minimal boilerplate",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gpereyra/school-of-prompt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
        "anthropic": [
            "anthropic>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "school-of-prompt=school_of_prompt.cli:main",
        ],
    },
)