from pprint import pprint

import pandas as pd
import numpy as np
import datetime
import pytz
from typing import Union

def _simple(_df: pd.DataFrame, df_idx: list[Union[datetime.time,datetime.datetime]], raster_size: int) -> pd.DataFrame:
    start_end_pairs = _df[["start_idx", "end_idx", "wrap"]].values

    yvals = np.zeros(raster_size,dtype=np.int32)
    for start_idx, end_idx, wrap in start_end_pairs:
        vals = np.zeros(raster_size,dtype=np.int32)
        vals[end_idx] = -1
        vals[0] = wrap
        vals[start_idx] = 1
        yvals += np.cumsum(vals).astype(np.int32)

    raster_df = pd.DataFrame(yvals.astype(int),columns=["count"])
    raster_df.index = df_idx
    min_idx = _df["start_idx"].min()
    max_idx = _df["end_idx"].max()
    raster_df = raster_df[(raster_df.index >= df_idx[min_idx]) & (raster_df.index <= df_idx[max_idx])]
    return raster_df


def raster_timeframes(df: pd.DataFrame, resolution_sec: int,
                      start_ts_name: str = "start_ts", end_ts_name: str ="end_ts") -> pd.DataFrame:
    """
    :param df: DataFrame containing events from star_ts_name to end_ts_name; if idtype!=None, df must contain a column idtype with event location IDs
    :param resolution_sec: raster resolution in seconds
    :param start_ts_name: DataFrame column containing start datetime timestamp
    :param end_ts_name: DataFrame column containing end datetime timestamp
    :return: DataFrame with index "time" (containing all resolution_min-sized buckets) and either column "count" if idtype==None or columns df[idtype].unique()
    """

    num_slices = (60 * 60 * 24) // resolution_sec
    df_idx = [(datetime.datetime(2021, 1, 1, 0, 0, 0)
                               + datetime.timedelta(seconds=resolution_sec * x)).time()
                              for x in list(range(num_slices))]

    df[start_ts_name] = df[start_ts_name].dt.tz_convert("UTC")
    df[end_ts_name] = df[end_ts_name].dt.tz_convert("UTC")


    df["start_idx"] = pd.to_numeric(np.floor((  df[start_ts_name].dt.hour * 60 * 60
                                              + df[start_ts_name].dt.minute * 60
                                              + df[start_ts_name].dt.second)
                                             / resolution_sec),
                                    downcast="integer")
    df["end_idx"]   = pd.to_numeric(np.floor((  df[end_ts_name].dt.hour * 60 * 60
                                              + df[end_ts_name].dt.minute * 60
                                              + df[end_ts_name].dt.second)
                                             / resolution_sec),
                                    downcast="integer")

    # check if interval wraps around midnight
    df["wrap"] = (df[end_ts_name].dt.time < df[start_ts_name].dt.time) & (df.end_idx != 0)

    if len(df[df.wrap]):
        print(f"Warning: Data seems to cross midnight! This might break some of the following analyses.")

    raster_df = _simple(df, df_idx, num_slices)

    return raster_df
