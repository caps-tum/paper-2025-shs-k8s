import datetime
import functools
import typing

import dateutil.tz
import pytz

import pandas as pd

from typing import Optional, Callable, Union
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker
import matplotlib.dates
import matplotlib.lines
from pathlib import Path


from functionCacher.Cacher import Cacher
from mpl_toolkits.axes_grid1 import make_axes_locatable

from visualisation.utils import raster_timeframes
cacher = Cacher()

matplotlib.rc('font', **{
    'family' : 'sans',
    'size'   : 24})
#matplotlib.use('QtAgg')  # or can use 'TkAgg', whatever you have/prefer


pd.options.display.width = 1920
pd.options.display.max_columns = 99
pd.options.display.max_rows=99
pd.options.display.min_rows=99

from visualisation.classes import Measurement, OSURun


# courtesy to https://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix="B", digits: int = 0, space: str = " "):
    # units = ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi")
    units = ("", "k", "M", "G", "T", "P", "E", "Z")
    for unit in units:
        if abs(num) < 1024.0:
            return f"{num:3.{digits}f}{space}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def overview(measurement: Measurement,
             outpath: Path,
             save: bool = False,
             figsize: tuple[int,int] = (12,6)):
    df = measurement.to_df()

    batch_starts = [
        b.start_time for b in measurement.iterations[0]
    ]
    fig, ax = plt.subplots(figsize=figsize)


    batch_sizes = [len(b.launched_jobs)
                   for b in measurement.iterations[0]]
    ax.plot(batch_starts, batch_sizes)
    ax.vlines(batch_starts, 0, max(batch_sizes), alpha=.5)

    ax.yaxis.grid(True)
    ax.yaxis.grid(True, which="minor", alpha=.5)
    x_locator = matplotlib.dates.SecondLocator(interval=10)
    x_locator_minor = matplotlib.dates.SecondLocator(interval=1)
    date_format = "%M:%S"
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(date_format,
                                                                tz=pytz.timezone("Europe/Berlin")))
    ax.xaxis.set_major_locator(x_locator)
    ax.xaxis.set_minor_locator(x_locator_minor)

    fig.tight_layout()
    if save:
        plt.savefig(outpath / "overview.pdf")
    else:
        plt.show()

def active_jobs(measurements: list[Measurement],
                outpath: Path,
                save: bool = False,
                ramp: bool = False,
                x_locator_major = matplotlib.dates.SecondLocator(interval=5),
                x_locator_minor = matplotlib.dates.SecondLocator(interval=1),
                y_locator_major = matplotlib.ticker.AutoLocator(),
                y_locator_minor = matplotlib.ticker.MultipleLocator(10),
                figsize: tuple[int,int] = (12,6)):
    fig, ax = plt.subplots(figsize=figsize)

    for mi, measurement in enumerate(measurements):
        df = measurement.to_df()
        df["delta"] = np.clip(df["end_time"] - df["start_time"], a_min=0, a_max=None)
        first_start = df["batch_start_time"].min()

        df["corrected_start_time"] = pd.to_datetime(pytz.utc.localize(datetime.datetime(2000,1,1))) \
                                     + np.clip(df["start_time"] - first_start, a_min=0, a_max=None)
        df["corrected_end_time"] = df["corrected_start_time"] + df["delta"]

        raster_data = []
        max_n = 0
        for idx, group in df.groupby("iteration"):
            raster = raster_timeframes(group, resolution_sec=1,
                                       start_ts_name="corrected_start_time",
                                       end_ts_name="corrected_end_time")
            raster_data.append(raster["count"].values.tolist())
            max_n = max(max_n, len(raster))


        for i in range(len(raster_data)):
            raster_data[i] = np.pad(raster_data[i],(0,max_n-len(raster_data[i])), constant_values=(0))
        raster_data = np.array(raster_data)
        y = raster_data.reshape((raster_data.shape[0], raster_data.shape[1])).mean(axis=0)
        x = [datetime.datetime(2000,1,1) + datetime.timedelta(seconds=i)
                 for i in range(len(y))]
        ax.plot(x, y, label=measurement.type)

        y05 = np.quantile(raster_data, 0.05, axis=0)
        y95 = np.quantile(raster_data, 0.95, axis=0)

        ax.fill_between(x, y05, y95, alpha=0.1)

    if ramp:
        df = measurements[0].to_df()
        df_i0 = df[df.iteration == 0]
        start_times = df_i0.groupby("batch_id").batch_start_time.first()
        start_times = start_times - start_times[0]
        start_times = [datetime.datetime(2000,1,1) + s for s in start_times]
        batch_sizes = [len(b.launched_jobs)
                       for b in measurements[0].iterations[0]]

        ax2: plt.Axes = ax.twinx()
        ax2.plot(start_times, batch_sizes, color="tab:green",
                 label="# jobs", marker=".",zorder=3)
        ax2.set_ylabel("Submitted Jobs per Batch")

        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, ncols=3)
    else:
        ax.legend()

    ax.yaxis.grid(True, which="major")
    ax.yaxis.grid(True, which="minor", alpha=.4, linestyle="--")
    ax.xaxis.grid(True, which="major", alpha=0.5, linewidth=0.75)

    date_format = "%M:%S"
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(date_format, tz=dateutil.tz.tzlocal()))
    ax.xaxis.set_major_locator(x_locator_major)
    ax.xaxis.set_minor_locator(x_locator_minor)

    ax.yaxis.set_major_locator(y_locator_major)
    ax.yaxis.set_minor_locator(y_locator_minor)
    ax.set_ylabel("Running Jobs")
    ax.set_xlabel("Time since Measurement Start")
    # ax.tick_params(axis='x', labelrotation=40, ha="right")
    ax.set_xticks(ax.get_xticks(), labels=ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
    ax.set_ylim(bottom=0)


    fig.tight_layout()
    if save:
        plt.savefig(outpath / "active_jobs.pdf")
    else:
        plt.show()


def job_delay(measurements: list[Measurement],
              outpath: Path,
              save: bool = False,
              colors: list[str] = list(matplotlib.colors.TABLEAU_COLORS.keys()),
              y_locator_major=matplotlib.ticker.MultipleLocator(5 * 1e9),
              y_locator_minor=matplotlib.ticker.MultipleLocator(1 * 1e9),
              y_label: bool = True,
              figsize: tuple[int,int] = (12,6)):
    fig, ax = plt.subplots(figsize=figsize)

    medians = []
    for mi, measurement in enumerate(measurements):
        df = measurement.to_df()
        # start_time is second-granular, batch_start_time is microsecond-granular, which can lead to negative values
        #  so clip lower values to 0
        df["delay"] = (df["start_time"] - df["batch_start_time"]).clip(lower=pd.to_timedelta(0))
        b = ax.boxplot(df["delay"], label=measurement.type, positions=[mi], widths=0.7)
        for m in b["medians"]:
            m.set_color(colors[mi % len(colors)])
            m.set_linewidth(2)
            m.set_zorder(1)
        medians.append(df["delay"].median())

    ax.yaxis.grid(True)
    ax.yaxis.grid(True, which="minor", alpha=.5)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: int(datetime.timedelta(microseconds=x/1000).total_seconds())))

    ax.yaxis.set_major_locator(y_locator_major)
    ax.yaxis.set_minor_locator(y_locator_minor)

    if y_label:
        ax.set_ylabel("Admission Delay (s)")
    ax.set_xticks(ax.get_xticks(), [m.type for m in measurements])

    fig.tight_layout()
    if save:
        plt.savefig(outpath / "job_delay.pdf")
        with open(outpath / "job_delay.meta", "w") as f:
            f.write("\n".join([f"Median {t.type}: {m} ({m.total_seconds()}s)" for m, t in zip(medians, measurements)]))
    else:
        plt.show()


def job_delay_batch(measurements: list[Measurement],
                    outpath: Path,
                    save: bool = False,
                    ramp: bool = False,
                    legend_loc = "upper center",
                    x_locator_major=matplotlib.ticker.MultipleLocator(5),
                    x_locator_minor=matplotlib.ticker.MultipleLocator(1),
                    y_locator_major=matplotlib.ticker.MultipleLocator(5*1e9),
                    y_locator_minor=matplotlib.ticker.MultipleLocator(1*1e9),
                    legend_ncols = 3,
                    figsize: tuple[int,int] = (12,6)):
    fig, ax = plt.subplots(figsize=figsize)
    for mi, measurement in enumerate(measurements):

            df = measurement.to_df()
            # start_time is second-granular, batch_start_time is microsecond-granular, which can lead to negative values
            #  so clip lower values to 0
            df["delay"] = (df["start_time"] - df["batch_start_time"]).clip(lower=pd.to_timedelta(0))

            y = df.groupby("batch_id")["delay"].mean()
            y05 = df.groupby("batch_id")["delay"].quantile(0.05)
            y95 = df.groupby("batch_id")["delay"].quantile(0.95)

            ax.plot(y, label=measurement.type, marker=".")
            ax.fill_between(list(range(len(y))), y05, y95,alpha=0.1)

    if ramp:
        df = measurements[0].to_df()
        df_i0 = df[df.iteration == 0]
        start_times = df_i0.groupby("batch_id").batch_id.first()

        batch_sizes = [len(b.launched_jobs)
                       for b in measurements[0].iterations[0]]

        ax2: plt.Axes = ax.twinx()
        ax2.plot(start_times, batch_sizes, color="tab:green",
                 label="# jobs", marker=".", zorder=3)
        ax2.set_ylabel("Submitted Jobs per Batch")

        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc=legend_loc, ncols=legend_ncols)
    else:
        ax.legend()

    ax.yaxis.grid(True, which="major")
    ax.yaxis.grid(True, which="minor", alpha=.4, linestyle="--")
    ax.xaxis.grid(True, which="major", alpha=0.5, linewidth=0.75)
    ax.xaxis.grid(True, which="minor", alpha=.4, linestyle="--")

    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: int(datetime.timedelta(microseconds=x/1000).total_seconds())))

    ax.xaxis.set_major_locator(x_locator_major)
    ax.xaxis.set_minor_locator(x_locator_minor)

    ax.yaxis.set_major_locator(y_locator_major)
    ax.yaxis.set_minor_locator(y_locator_minor)

    ax.set_xlabel("Batch ID")
    ax.set_ylabel("Admission Delay (s)")
    # ax.tick_params(axis='x', labelrotation=90)


    fig.tight_layout()
    if save:
        plt.savefig(outpath / "job_delay_batch.pdf")
    else:
        plt.show()


def job_delay_overhead(baseline: Measurement, measurements: list[Measurement],
                       outpath: Path,
                       save: bool = False,
                       figsize: tuple[int,int] = (12,6)):
    fig, ax = plt.subplots(figsize=figsize)
    df_baseline = baseline.to_df()
    # start_time is second-granular, batch_start_time is microsecond-granular, which can lead to negative values
    #  so clip lower values to 0
    df_baseline["delay"] = (df_baseline["start_time"] - df_baseline["batch_start_time"]).clip(lower=pd.to_timedelta(0))
    baseline_mean = df_baseline.groupby("batch_id")["delay"].mean()

    for mi, measurement in enumerate(measurements):
            df = measurement.to_df()
            # start_time is second-granular, batch_start_time is microsecond-granular, which can lead to negative values
            #  so clip lower values to 0
            df["delay"] = (df["start_time"] - df["batch_start_time"]).clip(lower=pd.to_timedelta(0))

            groups = df.groupby("batch_id")["delay"]
            safe_div = lambda a,b: np.divide(a, b, out=np.zeros_like(a), where=~np.isclose(b,np.zeros_like(b)))
            diff05 = safe_div(groups.quantile(.05).dt.total_seconds(), baseline_mean.dt.total_seconds())-1
            diff95 = safe_div(groups.quantile(.95).dt.total_seconds(), baseline_mean.dt.total_seconds())-1
            ax.fill_between(list(range(len(diff05))), diff05, diff95, alpha=0.1)

            diff = safe_div(groups.mean().dt.total_seconds(), baseline_mean.dt.total_seconds())-1
            ax.plot(diff, label=measurement.type)

    ax.yaxis.grid(True, which="major")
    ax.yaxis.grid(True, which="minor", alpha=.4, linestyle="--")
    ax.xaxis.grid(True, which="major", alpha=0.5, linewidth=0.75)

    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1))
    ax.set_xlabel("Batch Number")
    ax.set_ylabel("Startup Delay Overhead")
    ax.tick_params(axis='x', labelrotation=90)

    ax.legend()

    fig.tight_layout()
    if save:
        plt.savefig(outpath / "job_delay_overhead.pdf")
    else:
        plt.show()



def lineplot_osu(run_baseline: OSURun,
                 run_b: list[OSURun],
                 basepath: Path,
                 metric: Union[Union[str, Callable], list[Union[str, Callable]]],
                 metric_name: str = "",
                 mode: str = "",
                 error_q: float = 0.1,
                 y_decimals: int = 2,
                 xlabel: str = "",
                 save: bool = False,
                 title: bool = True,
                 y_lim: Optional[tuple[float,float]] = None,
                 y_minor_locator = matplotlib.ticker.MultipleLocator(0.005),
                 y_major_locator = matplotlib.ticker.MultipleLocator(0.01),
                 figsize: tuple[int, int] = (12, 8),
                 y_log_base: int = 10,
                 y_max: Optional[float] = None,
                 fname: Optional[str] = None):
    """
    Visualise benchmark Runs as linesplot.

    :param run_baseline: Baseline Run
    :param run_b: List of measurement Runs, compared against baseline Run
    :param metric: which metric to plot (str for simple key, depends on importer, or callable on a DataFrame for more complex lookups), can also be list of metrics
    :param metric_name: metric name to plot on yaxis
    :param mode: evaluation modes - "speedup", "delta", None
    :param error_q: percentile for error bars, [0,1]
    :param y_decimals: number of decimals for y-axis label
    :param basepath: basepath to store figure output to
    :param out_dir: output directory
    :param save: whether to save plot to file (will plt.show() on false)
    :param title: whether to add title
    :param figsize: matplotlib figure size
    :param fname: optional figure name suffix
    """
    if not isinstance(metric, list):
        metric = [metric]

    fig, ax = plt.subplots(ncols=1, figsize=figsize)

    fig: plt.Figure
    _metric_name = metric_name

    orig_shape = run_baseline.df.loc[1, :].shape
    data_baseline = np.array(run_baseline.df[metric[0]]).reshape((-1, orig_shape[0])).T
    data_baseline_mean = np.mean(data_baseline, axis=1)
    xlabels = list(run_baseline.df.loc[1, :].index)

    overall_min = 0
    overall_max = 0
    plot_metadata = ""
    if mode == "delta":
        for r_i, run in enumerate(run_b + [run_baseline]):
            data_b = np.array(run.df[metric[0]]).reshape((-1, orig_shape[0])).T

            diff = np.mean(data_b, axis=1) - data_baseline_mean

            diff_min = np.quantile(data_b, q=error_q, axis=1) - data_baseline_mean
            diff_max = np.quantile(data_b, q=1 - error_q, axis=1) - data_baseline_mean

            ax.plot(diff, label=f"{run.tag}")
            ax.fill_between(np.arange(len(diff)), diff_min, diff_max, alpha=.25)
            _metric_name = f"Δ"

    elif mode == "speedup" or mode == "speedup_inverse":
        inverse = mode == "speedup_inverse"
        for r_i, run in enumerate(run_b):
            data_b = np.array(run.df[metric[0]]).reshape((-1, orig_shape[0])).T

            data_b_mean = np.mean(data_b, axis=1)
            if inverse:
                speedup = (data_baseline_mean / data_b_mean) - 1
                speedup_min = (data_baseline_mean / np.quantile(data_b, q=error_q, axis=1)) - 1
                speedup_max = (data_baseline_mean / np.quantile(data_b, q=1 - error_q, axis=1)) - 1
            else:
                speedup = (data_b_mean / data_baseline_mean) - 1
                speedup_min = (np.quantile(data_b, q=error_q, axis=1) / data_baseline_mean) - 1
                speedup_max = (np.quantile(data_b, q=1 - error_q, axis=1) / data_baseline_mean) - 1

            ax.plot(speedup, label=f"{run.tag}", marker=".")
            _metric_name = f"overhead"
            ax.fill_between(np.arange(len(speedup)), speedup_min, speedup_max, alpha=.25)
            ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(xmax=1, decimals=y_decimals))

            plot_metadata += f"Run {run.tag}: {np.average(speedup) * 100:.2f}% " \
                             f"({np.quantile(speedup, error_q) * 100:.2f}%, {np.quantile(speedup, 1 - error_q) * 100:.2f}%)\n"
            overall_min = min(overall_min, min(speedup_min))
            overall_max = max(overall_max, max(speedup_max))

    else:
        for r_i, r in enumerate(run_b + [run_baseline]):
            data = np.array(r.df[metric[0]]).reshape((-1, orig_shape[0])).T
            data_mean = np.mean(data, axis=1)
            ax.errorbar(x=np.arange(len(data_mean)),
                        y=data_mean,
                        yerr=[np.clip(data_mean - np.min(data, axis=1), a_min=0, a_max=None),
                              np.clip(np.max(data, axis=1) - data_mean, a_min=0, a_max=None)],
                        label=f"{r.tag}", marker=".")
            ax.set_yscale("log", base=y_log_base)
            ax.set_ylim(bottom=1)

    _,xlim_r = ax.get_xlim()
    ax.set_xlim(left=-0.25, right=xlim_r-1+0.25)
    xlabels_fmt = list(map(sizeof_fmt, xlabels))
    ax.set_xticks(np.arange(orig_shape[0]), xlabels_fmt, rotation=45, ha="right")
    ax.yaxis.set_minor_locator(y_minor_locator)
    ax.yaxis.set_major_locator(y_major_locator)


    if title:
        ax.set_title(run_baseline.name.split(" ")[0])
    if metric_name != "":
        ax.set_ylabel(metric_name)
    if y_max:
        ax.set_ylim(top=y_max)
    if xlabel != "":
        ax.set_xlabel(xlabel)
    if y_lim != None:
        ax.set_ylim(*y_lim)
    ax.yaxis.grid(True, which="major")
    ax.yaxis.grid(True, which="minor", alpha=.4, linestyle="--")
    ax.xaxis.grid(True, which="major", alpha=0.5, linewidth=0.75)
    ax.legend(ncols=3)

    fig.tight_layout(pad=0)

    if save:
        prefix = f"{fname}_" if isinstance(fname, str) else ""
        output_dir = basepath / "figures"
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
        plt.savefig(output_dir / f"{prefix}{run_baseline.name.split(' ')[0]}.pdf")

        meta_output_dir = basepath / "meta"
        if not meta_output_dir.is_dir():
            meta_output_dir.mkdir(parents=True)
        with open(meta_output_dir / f"{prefix}{run_baseline.name.split(' ')[0]}.meta", "w") as out:
            out.write(plot_metadata)
    else:
        plt.show()
