import pandas as pd
import numpy as np
import datetime
from dataclasses import dataclass

@dataclass
class Job:
    name: str
    start_time: datetime.datetime
    end_time: datetime.datetime

@dataclass
class Batch:
    launched_jobs: list[Job]
    start_time: datetime.datetime

@dataclass
class Measurement:
    iterations: list[list[Batch]]
    meta: str
    type: str

    def to_df(self) -> pd.DataFrame:
        data = []

        for i, iteration in enumerate(self.iterations):
            for bid, batch in enumerate(iteration):
                for job in batch.launched_jobs:
                    data.append({
                        "job": job.name,
                        "start_time": job.start_time,
                        "end_time": job.end_time,
                        "batch_id": bid,
                        "batch_start_time": batch.start_time,
                        "iteration": i,
                    })

        return pd.DataFrame(data)




@dataclass
class OSURun:
    name: str
    df: pd.DataFrame
    binary: str = ""
    meta: str = ""
    tag: str = ""

    def concat(self, other_run):
        self.df = pd.concat([self.df, other_run.df])
        return self

    def merge(self, other_run):
        _vals = np.array([self.df.values, other_run.df.values])
        self.df = pd.DataFrame(np.mean(_vals, axis=0))
        return self

    def set_name(self, name: str):
        self.name = name
        return self
