import pathlib

from pprint import pprint

import matplotlib.dates
import matplotlib.ticker
import pandas as pd

import visualisation.loader
import visualisation.visualise


def ramp(basepath_data: pathlib.Path,
         basepath_figures: pathlib.Path,
         save: bool):
    m1 = visualisation.loader.load_measurement(basepath_data / "stresstest" /
                         "measurements_25-04-19T1006", type="vni:false")

    m2 = visualisation.loader.load_measurement(basepath_data / "stresstest" /
                         "measurements_25-04-20T1154", type="vni:true")


    # Figure 9
    visualisation.visualise.active_jobs([m2,m1],
                                        outpath=basepath_figures,
                                        save=save, ramp=True,
                                        x_locator_major=matplotlib.dates.SecondLocator([5 * i for i in range(60 // 5)]),
                                        x_locator_minor=matplotlib.dates.SecondLocator(range(60)),
                                        y_locator_minor=matplotlib.ticker.MultipleLocator(5),
                                        )
    # Figure 10
    visualisation.visualise.job_delay_batch([m2, m1],
                                            outpath=basepath_figures,
                                            save=save, ramp=True,
                                            legend_ncols=1, legend_loc="upper left")


    # Figure 12a
    visualisation.visualise.job_delay([m2,m1],
                                      outpath=basepath_figures,
                                      save=save,
                                      y_locator_major=matplotlib.ticker.MultipleLocator(5 * 1e9),
                                      y_locator_minor=matplotlib.ticker.MultipleLocator(1 * 1e9),
                                      figsize=(5,5))

    return



def spike(basepath_data: pathlib.Path,
         basepath_figures: pathlib.Path,
          save: bool):
    m1 = visualisation.loader.load_measurement(basepath_data / "stresstest" /
                          "measurements_25-04-19T1039", type="vni:false")

    m2 = visualisation.loader.load_measurement(basepath_data / "stresstest" /
                          "measurements_25-04-20T1206", type="vni:true")

    # Figure 11
    visualisation.visualise.active_jobs([m2,m1],
                                        outpath=basepath_figures,
                                        save=save,
                                        x_locator_major=matplotlib.dates.SecondLocator([15,30,45,0]),
                                        x_locator_minor=matplotlib.dates.SecondLocator([5*i for i in range(60//5)]),
                                        y_locator_minor=matplotlib.ticker.MultipleLocator(25),
                                        )

    # Figure 12b
    visualisation.visualise.job_delay([m2,m1],
                                      outpath=basepath_figures,
                                      save=save,
                                      figsize=(5,5),
                                      y_label=False,
                                      y_locator_major=matplotlib.ticker.MultipleLocator(20 * 1e9),
                                      y_locator_minor=matplotlib.ticker.MultipleLocator(5 * 1e9),
                                      )
    return


def osu(basepath_data: pathlib.Path, basepath_figures: pathlib.Path, save: bool):
    container_lat_vni = visualisation.loader.load_osu(folder="measurements_lm-mpi-job-mpilauncher-0_osu_latency_25-07-30T1311",
                                                      basepath_data=basepath_data / "osu" / "container", tag="vni:true")
    container_bw_vni = visualisation.loader.load_osu(folder="measurements_lm-mpi-job-mpilauncher-0_osu_bw_25-07-30T1409",
                                                     basepath_data=basepath_data / "osu" / "container", tag="vni:true")

    container_lat = visualisation.loader.load_osu(folder="measurements_lm-mpi-job-mpilauncher-0_osu_latency_25-07-30T1350",
                                                  basepath_data=basepath_data / "osu" / "container", tag="vni:false")
    container_bw = visualisation.loader.load_osu(folder="measurements_lm-mpi-job-mpilauncher-0_osu_bw_25-07-30T1352",
                                                 basepath_data=basepath_data / "osu" / "container", tag="vni:false")



    host_lat = visualisation.loader.load_osu(folder="measurements_cn03_osu_latency_25-07-30T1502",
                                             basepath_data=basepath_data / "osu" / "host", tag="host")
    host_bw = visualisation.loader.load_osu(folder="measurements_cn03_osu_bw_25-07-30T1538",
                                            basepath_data=basepath_data / "osu" / "host", tag="host")


    # Figure 5
    visualisation.visualise.lineplot_osu(
        run_baseline=host_bw,
        run_b=[
            container_bw_vni,
            container_bw,
        ],
        basepath=basepath_figures, save=save, title=False, figsize=(12, 5),
        mode="",
        y_decimals=0,
        metric_name="Throughput (MB/s)",
        metric="Bandwidth (MB/s)",
        xlabel="Packet Size",
        fname="raw",
        y_major_locator=matplotlib.ticker.LogLocator(base=10),
        y_minor_locator=matplotlib.ticker.LogLocator(base=10, subs="auto"),
    )

    # Figure 6
    visualisation.visualise.lineplot_osu(
        run_baseline=host_lat,
        run_b=[
            container_lat_vni,
            container_lat,
            host_lat,
        ],
        basepath=basepath_figures, save=save, title=False, figsize=(12, 5),
        mode="speedup",
        metric="Latency (us)",
        metric_name="Overhead",
        xlabel="Packet Size",
        y_decimals=0,
        y_lim=(-.012, .012),
        y_major_locator=matplotlib.ticker.MultipleLocator(0.01),
        y_minor_locator=matplotlib.ticker.MultipleLocator(0.001),
        # metric_name="Latency Δ (μs)",
    )

    # Figure 7
    visualisation.visualise.lineplot_osu(
        run_baseline=host_lat,
        run_b=[
            container_lat_vni,
            container_lat,
        ],
        basepath=basepath_figures, save=save, title=False, figsize=(12, 5),
        mode="",
        metric="Latency (us)",
        metric_name="Latency (us)",
        xlabel="Packet Size",
        y_decimals=0,
        fname="raw",
        y_major_locator=matplotlib.ticker.LogLocator(),
        y_minor_locator=matplotlib.ticker.LogLocator(subs="auto"),
    )

    # Figure 8
    visualisation.visualise.lineplot_osu(
            run_baseline=host_bw,
            run_b=[
                container_bw_vni,
                container_bw,
                host_bw,
            ],
            basepath=basepath_figures, save=save, title=False, figsize=(12,5),
            mode="speedup_inverse",
            y_decimals=0,
            y_lim=(-.018,.015),
            y_major_locator=matplotlib.ticker.MultipleLocator(0.01),
            y_minor_locator=matplotlib.ticker.MultipleLocator(0.001),
            metric_name="Overhead",
            metric="Bandwidth (MB/s)",
            xlabel="Packet Size",
        )




    # container_bw_get_vni = visualisation.loader.load_osu(folder="measurements_lm-mpi-job-mpilauncher-0_osu_get_bw_25-08-05T1058",
    #                                              basepath_data=basepath_data / "osu" / "container", tag="vni:true")
    # container_bw_get = visualisation.loader.load_osu(folder="measurements_lm-mpi-job-mpilauncher-0_osu_get_bw_25-08-05T1103",
    #                                              basepath_data=basepath_data / "osu" / "container", tag="vni:false")
    # host_bw_get = visualisation.loader.load_osu(folder="measurements_cn03_osu_get_bw_25-08-05T1312",
    #                                         basepath_data=basepath_data / "osu" / "host", tag="host")
    #
    # visualisation.visualise.lineplot_osu(
    #     run_baseline=host_bw_get,
    #     run_b=[
    #         container_bw_get_vni,
    #         container_bw_get,
    #         host_bw_get,
    #     ],
    #     basepath=basepath_figures, save=save, title=False, figsize=(12, 5),
    #     mode="speedup_inverse",
    #     y_decimals=0,
    #     y_major_locator=matplotlib.ticker.MultipleLocator(0.05),
    #     y_minor_locator=matplotlib.ticker.MultipleLocator(0.01),
    #     metric_name="Overhead",
    #     metric="Bandwidth (MB/s)",
    #     xlabel="Packet Size",
    # )

if __name__ == '__main__':
    basepath_data = pathlib.Path(__file__).parent.parent.absolute() / "data"
    basepath_figures = pathlib.Path(__file__).parent.parent.absolute() / "figures"

    if not basepath_figures.exists():
        basepath_figures.mkdir()

    save = True

    osu(basepath_data=basepath_data, basepath_figures=basepath_figures / "osu", save=save)
    # ramp(basepath_data=basepath_data, basepath_figures=basepath_figures / "ramp", save=save)
    # spike(basepath_data=basepath_data, basepath_figures=basepath_figures / "spike", save=save)
