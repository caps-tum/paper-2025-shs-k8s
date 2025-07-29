import io
import pathlib
from pathlib import Path
import datetime
import re

import pytz
import json
import gzip
import dateutil.tz
from pprint import pprint
import pandas as pd

from functionCacher.Cacher import Cacher
cacher = Cacher()

from visualisation.classes import Measurement, Batch, Job, OSURun

# tz = pytz.timezone('Europe/Berlin')
tz = dateutil.tz.tzlocal()
def load_measurement(measurement_dir: pathlib.Path, type: str) -> Measurement:
    with open(measurement_dir / "meta.md", "r") as infile:
        meta = infile.read()
    numiter = int(re.search(r"NUMITER\s+: (\d+)", meta, re.MULTILINE).group(1))

    iterations = []
    for i in range(1,numiter+1):
        with open(measurement_dir / f"{i}-job_data", "r") as infile:
            lines = infile.readlines()
            launched_jobs = list(
                map(str.strip,
                    lines[0].split(": ")[1].split(" ")))
            batch_sizes = list(
                map(int,
                    map(str.strip,
                        lines[1].split(": ")[1].split(" "))))
            start_times = list(
                map(lambda s: datetime.datetime.fromtimestamp(int(s)/1000, tz=pytz.utc).astimezone(tz),
                    map(str.strip,
                        lines[2].split(": ")[1].split(" "))))


        with (gzip.open(measurement_dir / f"{i}-job_output.json.gz", "r") as infile):
            job_info = json.load(infile)

            indexed_job_info = {}
            for job in job_info["items"]:
                if job["involvedObject"]["kind"] != "Job":
                    continue
                name = job["involvedObject"]["name"]
                if name not in indexed_job_info:
                    indexed_job_info[name] = {
                        "startTime": datetime.datetime(3000,1,1, tzinfo=tz),
                    }
                if job["message"] == "Job completed":
                    indexed_job_info[name]["completionTime"] = datetime.datetime.fromisoformat(job["lastTimestamp"]).astimezone(tz)
                elif "Created" in job["message"]:
                    indexed_job_info[name]["startTime"] = min(datetime.datetime.fromisoformat(job["firstTimestamp"]).astimezone(tz),
                                                        indexed_job_info[name]["startTime"])

        batches = []
        job_i = 0
        for i, batch_size in enumerate(batch_sizes):
            jobs = []
            for job in launched_jobs[job_i:job_i+batch_size]:
                jobName = job.split("/")[1]
                j = Job(name=jobName,
                        start_time=indexed_job_info[jobName]["startTime"],
                        end_time=indexed_job_info[jobName]["completionTime"]
                )
                jobs.append(j)

            batch = Batch(launched_jobs=jobs,
                          start_time=start_times[i])
            batches.append(batch)
            job_i += batch_size
        iterations.append(batches)


    return Measurement(iterations=iterations, meta=meta, type=type)


# @cacher.cache
def load_osu(folder: str, basepath_data: Path, **kwargs) -> OSURun:
    dfs = []
    name = ""
    with open(basepath_data / folder / "meta.md", "r") as infile:
        content = infile.read()
        name = re.compile(r"Binary: `.*\/(.*?)`").search(content).group(1) + " "

    file_dir = basepath_data / folder
    if kwargs.get("profile"):
        file_dir = file_dir / f'profile_{kwargs.get("profile")}'

    for file in list(filter(lambda x: x.suffix == ".dat", file_dir.iterdir())):
        with open(file, "r") as infile:
            # if int(file.stem.split("_")[1]) > 4: continue
            lines = infile.readlines()
            rdma_idx = -1
            if kwargs.get("pid", False):
                pid = int(lines[0])

            lines = lines[1:]
            for idx, line in enumerate(lines):
                if line.startswith("# Size"):
                    rdma_idx = idx
                    break
            if rdma_idx == -1:
                raise IndexError(f"Could not find '# Size' in {file}")
            measurement_lines = lines[rdma_idx:]
            if measurement_lines[1].startswith("#"):
                measurement_lines = [measurement_lines[0]] + measurement_lines[2:]
            sio = io.StringIO()
            pattern = re.compile(r"(\s{2,})")
            for line in measurement_lines:
                sio.write(re.sub(pattern, "\\t", line).lstrip())
            sio.seek(0)
            df = pd.read_csv(sio, sep="\t")
            df.insert(loc=len(df.columns) - 1, column="i", value=int(file.stem.split("_")[1]))
            dfs.append(df)
    out_df = pd.concat(dfs).set_index(["i", df.columns[0]]).sort_index()


    return OSURun(df=out_df, name=name, tag=kwargs.get("tag", ""))



def load_measurement_old(measurement_dir: pathlib.Path, type: str) -> Measurement:
    with open(measurement_dir / "meta.md", "r") as infile:
        meta = infile.read()
    numiter = int(re.search(r"NUMITER\s+: (\d+)", meta, re.MULTILINE).group(1))

    iterations = []
    for i in range(1,numiter+1):
        with open(measurement_dir / f"{i}-job_data", "r") as infile:
            lines = infile.readlines()
            launched_jobs = list(
                map(str.strip,
                    lines[0].split(": ")[1].split(" ")))
            batch_sizes = list(
                map(int,
                    map(str.strip,
                        lines[1].split(": ")[1].split(" "))))
            start_times = list(
                map(lambda s: datetime.datetime.fromtimestamp(int(s)/1000, tz=pytz.utc).astimezone(tz),
                    map(str.strip,
                        lines[2].split(": ")[1].split(" "))))

            clean_start = datetime.datetime.fromtimestamp(int(lines[3].split(": ")[1]), tz=pytz.utc)
            clean_end = datetime.datetime.fromtimestamp(int(lines[4].split(": ")[1]), tz=pytz.utc)


        with gzip.open(measurement_dir / f"{i}-job_output.json.gz", "r") as infile:
            job_info = json.load(infile)

            indexed_job_info = {
                job["metadata"]["name"]: job
                for job in job_info["items"]
            }
        batches = []
        job_i = 0
        for i, batch_size in enumerate(batch_sizes):
            jobs = []
            for job in launched_jobs[job_i:job_i+batch_size]:
                jobName = job.split("/")[1]
                j = Job(name=jobName,
                        start_time=datetime.datetime.fromisoformat(indexed_job_info[jobName]["status"]["startTime"]).astimezone(tz),
                        end_time=datetime.datetime.fromisoformat(indexed_job_info[jobName]["status"]["completionTime"]).astimezone(tz)
                )
                jobs.append(j)

            batch = Batch(launched_jobs=jobs,
                          start_time=start_times[i])
            batches.append(batch)
            job_i += batch_size
        iterations.append(batches)


    return Measurement(iterations=iterations, meta=meta, type=type)