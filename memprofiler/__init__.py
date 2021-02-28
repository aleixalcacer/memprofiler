from .memprofiler import MemProfiler


def load_ipython_extension(ipython):
    ipython.register_magics(MemProfiler)
    ipython.run_cell("from memprofiler import MemProfiler")
