from .memprofiler import MemProfiler


def load_ipython_extension(ipython):
    ipython.register_magics(MemProfiler)
