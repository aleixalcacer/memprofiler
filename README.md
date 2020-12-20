# memprofiler

![PyPI](https://img.shields.io/pypi/v/memprofiler)
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/aleixalcacer/memprofiler/HEAD?filepath=examples/)

memprofiler is a simple extension for monitoring memory usage of Jupyter notebook cells.


## Installation

It can be installed as a typical Python source package from PyPi using pip:

```
pip install memprofiler
```


## Usage

A basic example of how to use this extension can be found in
[this interactive Jupyter notebook](https://mybinder.org/v2/gh/aleixalcacer/memprofiler/HEAD?filepath=examples/basic.ipynb).


## Reference

### mprof_run

*%%mprof_run [-i INTERVAL] [-p] profile_id*

Run memory profiler during cell execution. (*cell_magic*)

- positional arguments:
    - *profile_id* \
        Profile identifier to label the results.

- optional arguments:

    - *-i INTERVAL*, *--interval INTERVAL* \
        Sampling period (in seconds), default 0.01.

    - *-p*, *--plot* \
        Plot the memory profile.


### mprof_plot

*%mprof_plot [-t TITLE] profile_ids [profile_ids ...]*

Plot memory profiler results. (*line_magic*)

- positional arguments:
    - *profile_ids* \
        Profile identifiers made by mprof_run. Supports regex.


## Contributing

Contributions are what make the open source community such an amazing place to be learn,
inspire, and create. Any contributions you make are **greatly appreciated**!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## License

Distributed under the BSD 3-Clause License.
See [LICENSE](https://github.com/aleixalcacer/memprofiler/blob/HEAD/LICENSE) for more information.


## Acknowledgements

- [@FrancescAlted](https://github.com/FrancescAlted)
