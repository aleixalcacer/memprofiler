# memprofiler

`memprofiler` is a light-weight extension for monitoring memory usage of Jupyter notebook cells.


## Installation

It can be installed as a typical Python source package from PyPi using pip:

```
pip install memprofiler
```

## Usage

TODO


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



## Contributing

Contributions are what make the open source community such an amazing place to be learn,
inspire, and create. Any contributions you make are **greatly appreciated**!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
