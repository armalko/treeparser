import setuptools

setuptools.setup(
    name="treeparser",
    version="0.1",
    author="armalko",
    author_email="metraoklam@gmail.com",
    description="Package to parse files and libraries",
    url="https://github.com/mal9/treeparser",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)