import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pumpy",
    version="0.0.1",
    author="Kydlaw",
    author_email="kydlawj@pm.me",
    description="A Tweepy interface to collect tweets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Kydlaw/pumpy",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU License",
        "Operating System :: OS Independent",
    ],
    install_requires=["loguru", "path.py", "pymongo", "tweepy"],
    python_requires=">=3.6",
)

