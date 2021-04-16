from setuptools import setup


CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Topic :: Software Development :: Libraries :: Python Modules
"""


setup(
    name="memprofiler",
    description="A simple IPython extension for monitoring memory usage of Jupyter notebook cells.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="BSD (3-clause)",
    version="0.1.7",
    author="Aleix Alcacer",
    author_email="aleixalcacer@gmail.com",
    url="https://github.com/aleixalcacer/memprofiler",
    packages=["memprofiler"],
    install_requires=["psutil", "ipython", "plotly"],
    python_requires=">=3.4",
    classifiers=list(filter(None, CLASSIFIERS.split("\n"))),
)
