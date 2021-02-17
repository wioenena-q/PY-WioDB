from setuptools import setup




with open("README.md", "r") as file:
    README = file.read()
    file.close()



setup(
    name="wiodb",
    version="0.0.5",
    author="wioenena.q",
    packages=["wiodb","wiodb.src"],
    keywords=["jsonDB", "wiodb", "database"],
    license="MIT",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/wioenena-q/wiodbForPython"
)
