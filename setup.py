from setuptools import setup


CLASSIFIERS =  """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
License :: Free To Use But Restricted
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Testing
"""


setup(
    name="memprofiler",
    description="A light-weight extension for monitoring memory usage of Jupyter notebook cells",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    version="2020.1.0",
    author="Aleix Alcacer",
    author_email="aleixalcacer@gmail.com",
    url="https://github.com/aleixalcacer/memprofiler",
    packages=["memprofiler"],
    install_requires=["psutil", "ipython", "plotly"],
    python_requires=">=3.4",
    classifiers=filter(None, CLASSIFIERS.split("\n")),
)
