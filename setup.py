from setuptools import setup


CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development
Operating System :: POSIX
Operating System :: Unix
"""


setup(
    name='memprofiler',
    description='A module for monitoring memory usage of IPython cells',
    long_description=open('README.md').read(),
    version="2020.1.0",
    author='Aleix Alcacer',
    author_email='aleixalcacer@gmail.com',
    url='https://github.com/aleixalcacer/memprofiler',
    packages=['memprofiler'],
    install_requires=['psutil', 'ipython', 'plotly'],
    python_requires='>=3.4',
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
    license=open('LICENSE').read()
)
