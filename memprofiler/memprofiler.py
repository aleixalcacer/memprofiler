from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring
from IPython import get_ipython
from multiprocessing import Process, Pipe, connection
import time
import psutil
import os
import matplotlib.pyplot as plt
import numpy as np


def get_current_memory(pid):
    process = psutil.Process(pid)
    mem = process.memory_info().rss
    return mem / 2 ** 20


def get_current_time():
    return time.time()


def sampling_memory(pipe: connection.Connection, pid, interval, start_memory):
    pipe.send(0)
    time_prof = get_current_time()
    memory_prof = []

    while True:
        memory_usage = get_current_memory(pid)
        memory_prof.append(memory_usage - start_memory)
        if pipe.poll(interval):
            break
    time_prof = get_current_time() - time_prof

    pipe.send(memory_prof)
    pipe.send(time_prof)


@magics_class
class MemProfiler(Magics):

    keep_sampling = False
    memory_profiles = {}
    time_deltas = {}
    current_memory_prof = None
    current_memory_delta = 0
    current_time_delta = 0
    current_label = None
    current_interval = 0.01
    ip = get_ipython()
    pid = os.getpid()

    def __init__(self, shell):
        super(MemProfiler, self).__init__(shell)
        self.ip.register_magic_function(self.mprof_run)

    @property
    def current_memory(self):
        return get_current_memory(self.pid)

    @property
    def current_time(self):
        return get_current_time()

    @cell_magic
    @magic_arguments()
    @argument('-i', '--interval', type=float, help='Sampling period (in seconds), defaults to 0.01', default=0.01)
    @argument('label', type=str, help='Memory profile label.')
    def mprof_run(self, line, cell):
        args = parse_argstring(self.mprof_run, line)
        self.current_interval = args.interval
        line = args.label

        import gc
        gc.collect()

        child_conn, parent_conn = Pipe()

        self.current_memory_delta = self.current_memory
        p = Process(target=sampling_memory,
                    args=(child_conn, self.pid, self.current_interval, self.current_memory_delta))
        p.daemon = True

        p.start()

        parent_conn.recv()  # start sampling memory
        self.ip.run_cell(cell)
        parent_conn.send(0)  # finish sampling memory

        self.current_memory_delta = self.current_memory - self.current_memory_delta

        self.current_memory_prof = parent_conn.recv()
        self.current_time_delta = parent_conn.recv()

        self.memory_profiles[line] = self.current_memory_prof
        self.time_deltas[line] = self.current_time_delta

        print(f"Memory usage: {self.current_memory_delta:.4f} MiB")
        print(f"Elapsed time: {self.current_time_delta:.4f} s")


    @line_magic
    @magic_arguments()
    @argument('profiles', type=str, help='Profiles labels.')
    def mprof_plot(self, line):
        labels = line.split()
        for key in labels:
            y = self.memory_profiles[key]
            x = np.linspace(0, self.time_deltas[key], len(y))
            plt.plot(x, y, label=key)


        plt.legend()
        plt.xlabel("Seconds (s)")
        plt.ylabel("MiB")

    @line_magic
    @magic_arguments()
    def mprof_clean(self, line):
        self.memory_profiles = {}
        self.time_deltas = {}
