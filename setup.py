import setuptools

PACKAGE = "simplenight-api"
# MUST BE PROPERLY SET. Folder name in src/
# bin/local-build interpolates package name for build purposes

with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name=PACKAGE,
    version="0.0.1",
    description="SIMPLENIGHT API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    install_requires=[
        "Django==3.0.6",
        "python-dateutil~=2.8",
    ],
    extras_require={
        "dev": [
            "bandit",
            "black",
            "flake8",
            "pytest",
            "pytest-cov",
            "pytest-mock",
            "python-dotenv",
            "tox",
            "pre-commit",
        ],
    },
    python_requires=">=3.7",
)
