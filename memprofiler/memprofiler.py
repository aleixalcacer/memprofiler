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
    time_start = current_time()
    memory_prof = []
    memory_start = current_memory(pid)

    while True:
        memory_prof.append(current_memory(pid) - memory_start)
        time_prof.append(current_time() - time_start)

        if pipe.poll(interval):  # Check if cell exec finishes
            break
    time_prof.append(current_time() - time_start)
    memory_prof.append(current_memory(pid) - memory_start)

    profile = {"m_prof": memory_prof,
               "m_peak": max(memory_prof),
               "m_delta": memory_prof[-1],
               "m_total": memory_prof[-1] + memory_start,
               "t_prof": time_prof,
               "t_delta": time_prof[-1]
               }
    pipe.send(profile)


@magics_class
class MemProfiler(Magics):

    profiles = {}
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

        profile = parent_conn.recv()
        self.profiles[line] = profile
        print(f"memprofiler: used {profile['m_delta']:.2f} MiB RAM "
              f"(peak of {profile['m_peak']:.2f} MiB) in {profile['t_delta']:.4f} s, "
              f"total RAM usage {profile['m_total']:.2f} MiB")

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
        keys = self.profiles.keys()
        matches = set()
        for regex in args.profile_ids:
            matches.update([string for string in keys if re.match(regex, string)])

        # Plot memory profiles
        fig = go.Figure()
        for key in sorted(matches):
            y = self.profiles[key]["m_prof"]
            x = self.profiles[key]["t_prof"]
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
