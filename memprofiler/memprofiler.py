from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring
from IPython import get_ipython
from multiprocessing import Process, Pipe, connection
import time
import psutil
import os
import plotly.graph_objects as go
import re


def current_memory(pid: int):
    process = psutil.Process(pid)
    mem = process.memory_info().rss
    return mem / 2 ** 20


def current_time():
    return time.time()


def sampling_memory(pipe: connection.Connection, pid: int, interval: float):
    pipe.send(0)  # Start sampling memory
    time_prof = []
    start_time = current_time()
    memory_prof = []
    start_memory = current_memory(pid)
    steps_prof = []
    while True:
        memory_prof.append(current_memory(pid) - start_memory)
        time_prof.append(current_time() - start_time)

        if pipe.poll(interval):  # Check if cell exec finishes
            data = pipe.recv()

            if isinstance(data, str):
                steps_prof.append(current_time() - start_time)
            else:
                break

    time_delta = current_time() - start_time
    memory_delta = current_memory(pid) - start_memory

    pipe.send((memory_prof, memory_delta, time_prof, time_delta))
    pipe.send(steps_prof)


@magics_class
class MemProfiler(Magics):

    memory_profiles = {}
    time_profiles = {}
    ip = get_ipython()

    def __init__(self, shell):
        super(MemProfiler, self).__init__(shell)

    @magic_arguments()
    @argument("-i", "--interval", type=float, help="Sampling period (in seconds), default 0.01.", default=0.01)
    @argument("-p", "--plot", action='store_true', help="Plot the memory profile.")
    @argument("profile_id", type=str, help="Profile identifier to label the results.")
    @cell_magic
    def mprof_run(self, line: str, cell: str):
        """Run memory profiler during cell execution. (*cell_magic*)"""
        args = parse_argstring(self.mprof_run, line)
        interval = args.interval
        line = args.profile_id

        child_conn, parent_conn = Pipe()

        p = Process(target=sampling_memory, args=(child_conn, os.getpid(), interval))
        p.daemon = True
        p.start()
        parent_conn.recv()  # Check if sampling process starts
        self.ip.run_cell(cell)
        parent_conn.send(0)  # Stop sampling memory

        memory_prof, memory_delta, time_prof, time_delta = parent_conn.recv()

        self.memory_profiles[line] = memory_prof
        self.time_profiles[line] = time_prof
        memory_peak = max(memory_prof)

        print(f"Memory profiler: Used {memory_delta:.4f} MiB "
              f"(peak of {memory_peak:.4f} MiB) in {time_delta:.4f} s")

        if args.plot:
            self.mprof_plot(line)

    @magic_arguments()
    @argument("-t", "--title", type=str, help="String shown as plot title.", default="Memory profile")
    @argument("profile_ids", type=str, nargs="+", help="Profile identifiers made by mprof_run. Supports regex.")
    @line_magic
    def mprof_plot(self, line: str):
        """Plot memory profiler results. (*line_magic*)"""
        args = parse_argstring(self.mprof_plot, line)

        # Find regex matches
        keys = self.memory_profiles.keys()
        matches = set()
        for regex in args.profile_ids:
            matches.update([string for string in keys if re.match(regex, string)])

        # Plot memory profiles
        fig = go.Figure()
        for key in matches:
            y = self.memory_profiles[key]
            x = self.time_profiles[key]
            fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=key))

        fig.update_layout(
            title={
                'text': args.title.replace("\"", "").replace("\'", ""),
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis_title="Time (in seconds)",
            yaxis_title="Memory used (in MiB)",
        )

        fig.show()
