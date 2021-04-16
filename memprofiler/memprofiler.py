from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring
from IPython import get_ipython
from multiprocessing import Process, Pipe, connection
import itertools
import time
import psutil
import os
import plotly.graph_objects as go
import plotly.express as px
from dataclasses import dataclass
import re
import gc


colors = px.colors.qualitative.Set1
dashes = ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
sep = "::"
tmp_id = "profile_id"


def line_chart(matches: list, args):
    l0 = "l0" if args.groupby == 1 else "l1"
    l1 = "l1" if args.groupby == 1 else "l0"

    fig = go.Figure()
    for i, (group, matches) in enumerate(matches):
        for j, e in enumerate(matches):
            x = e.time_prof
            y = e.memory_prof
            name = getattr(e, l0)
            if getattr(e, l1) != "":
                name += ": " + getattr(e, l1)

            fig.add_trace(go.Scatter(name=name,
                                     x=x,
                                     y=y,
                                     mode="lines",
                                     legendgroup=i,
                                     marker_color=colors[i],
                                     line=dict(dash=dashes[j])
                                     )
                          )

    fig.update_xaxes(title_text="Time (in seconds)")
    fig.update_yaxes(title_text="Memory used (in MiB)")
    return fig


def bar_chart(matches: list, args):
    l1 = "l1" if args.groupby == 1 else "l0"

    if args.variable == "time":
        attr = "time_delta"
        yaxes_title = "Time (in seconds)"
    else:
        attr = "memory_peak"
        yaxes_title = "Memory used (in MiB)"

    fig = go.Figure()
    for i, (group, matches) in enumerate(matches):
        y = [getattr(e, attr) for e in matches]
        x = [getattr(e, l1) for e in matches]
        fig.add_trace(go.Bar(name=group,
                             x=x,
                             y=y,
                             marker_color=colors[i],
                             )
                      )

    fig.update_yaxes(title_text=yaxes_title)
    fig.update_layout(
        barmode=args.barmode,
    )
    return fig


def update_layout(fig, args):
    fig.update_layout(
        title={
            'text': args.title.replace("\"", "").replace("\'", ""),
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=True
    )
    return fig


@dataclass
class Profile:
    l0: str
    l1: str
    memory_prof: list
    memory_peak: float
    memory_delta: float
    memory_total: float
    time_prof: list
    time_delta: float

    def __hash__(self):
        return hash((self.l0 + sep + self.l1))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.l0 + sep + self.l1 == other.l0 + sep + other.l1


def current_memory(pid: int):
    process = psutil.Process(pid)
    mem = process.memory_info().rss
    return mem / 2 ** 20


def current_time():
    return time.time()


def sampling_memory(pipe: connection.Connection, pid: int, interval: float, l0: str, l1: str):
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

    profile = Profile(l0,
                      l1,
                      memory_prof,
                      max(memory_prof),
                      memory_prof[-1],
                      memory_prof[-1] + memory_start,
                      time_prof,
                      time_prof[-1])
    pipe.send(profile)


@magics_class
class MemProfiler(Magics):

    profiles = {}
    ip = get_ipython()

    def __init__(self, shell):
        super(MemProfiler, self).__init__(shell)


    @magic_arguments()
    @argument("-q", "--quiet",
              action='store_true',
              help="Suppress verbosity.")
    @argument("-i", "--interval",
              type=float,
              help="Sampling period (in seconds), default 0.01.",
              default=0.01)
    @argument("-p", "--plot",
              action='store_true',
              help="Plot the memory profile.")
    @argument("profile_id",
              nargs='?',
              help="Profile label. You can specify up to "
                   f"two keywords by separating them with {sep} (keyword0{sep}keyword1). "
                   "Only profile_ids with two keywords can be used in plot-related functions.")
    @cell_magic
    def mprof_run(self, line: str, cell: str):
        """Run memory profiler during cell execution. (*cell_magic*)"""
        args = parse_argstring(self.mprof_run, line)
        interval = args.interval

        line = args.profile_id
        if line is None:
            line = tmp_id
        else:
            line.replace("\"", "").replace("\'", "")

        if line.count(sep) > 1:
            raise AttributeError("The memory profile label is incorrect! "
                                 "See help for more info (%%mprof_run?).")

        line_tmp = line.split(sep)
        l0, l1 = "", ""
        if len(line_tmp) > 2:
            raise AttributeError
        elif len(line_tmp) == 2:
            l0, l1 = line_tmp[0], line_tmp[1]
        elif len(line_tmp) == 1:
            l0 = line_tmp[0]

        child_conn, parent_conn = Pipe()

        p = Process(target=sampling_memory, args=(child_conn, os.getpid(), interval, l0, l1))
        p.daemon = True

        gcold = gc.isenabled()
        if gcold:
            gc.collect()
        gc.disable()
        p.start()
        parent_conn.recv()  # Check if sampling process starts
        try:
            self.ip.run_cell(cell)
        finally:
            parent_conn.send(0)  # Stop sampling memory
        profile = parent_conn.recv()
        if gcold:
            gc.enable()

        self.profiles[profile.l0 + sep + profile.l1] = profile
        if not args.quiet:
            print(f"memprofiler: used {profile.memory_delta:.2f} MiB RAM "
                  f"(peak of {profile.memory_peak:.2f} MiB) in {profile.time_delta:.4f} s, "
                  f"total RAM usage {profile.memory_total:.2f} MiB")

        if args.plot:
            self.mprof_plot(line)

    @magic_arguments()
    @argument("-t", "--title",
              default="Memory profile",
              help="String shown as plot title.")
    @argument("--groupby",
              type=int,
              default=1,
              choices=[0, 1],
              help="Identifier number used to group the results, default 1.")
    @argument("profile_ids",
              nargs="+",
              help="Profile labels made by mprof_run. Supports regex.")
    @line_magic
    def mprof_plot(self, line: str):
        """Plot detailed memory profiler results. (*line_magic*)"""
        args = parse_argstring(self.mprof_plot, line)

        # Find regex matches
        matches = self.parse_regex(args.profile_ids, args)

        # Plot memory profiles
        fig = line_chart(matches, args)
        fig = update_layout(fig, args)
        fig.show()

    @magic_arguments()
    @argument("-t", "--title",
              default="Memory profile",
              help="String shown as plot title.")
    @argument("--variable",
              default='memory',
              choices=['time', 'memory'],
              help="Variable to plot, default \'memory\'.")
    @argument("--barmode",
              default='group',
              choices=['group', 'stack'],
              help="Bar char mode, default \'group\'.")
    @argument("--groupby",
              type=int,
              default=1,
              choices=[0, 1],
              help="Identifier number used to group the results, default 1.")
    @argument("profile_ids", nargs="+", help="Profile labels made by mprof_run. Supports regex.")
    @line_magic
    def mprof_barplot(self, line: str):
        """Plot only-memory or only-time results in a bar chart. (*line_magic*)"""
        args = parse_argstring(self.mprof_barplot, line)

        # Find regex matches
        matches = self.parse_regex(args.profile_ids, args)

        # Plot results
        fig = bar_chart(matches, args)
        fig = update_layout(fig, args)
        fig.show()

    def parse_regex(self, profile_ids, args):
        l0 = "l0" if args.groupby == 1 else "l1"
        l1 = "l1" if args.groupby == 1 else "l0"
        matches = set(itertools.chain.from_iterable([e for e in self.profiles.values() if re.match(regex, e.l0 + sep + e.l1)] for regex in profile_ids))
        groups = sorted(set(map(lambda x: getattr(x, l0), matches)))
        g_matches = [(g, sorted([x for x in matches if getattr(x, l0) == g], key=lambda x: (getattr(x, l0), getattr(x, l1)))) for g in groups]
        return g_matches
