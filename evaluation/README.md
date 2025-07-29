# Evaluation

This folder contains the shell script `stresstest.sh`, which performs the two types of evaluation described in the paper, namely `spike-test` and `ramp-test`. Run `./stresstest.sh --help` to get an overview of all options. Modify default values to your liking (especially the location of `kubectl` and the default output path). 

The following lists all commands used to generate the data for the figures reported in the paper. 

## Data Acquisition

The sections below describe how to run the benchmarks evaluated in the paper. The data presented in the paper is stored in this repository at `data/*`.

### Communication Overhead (OSU)

All files for the communicataion overhead evaluation are stored in `evaluation/osu`

#### Kubernetes

Run the file `evaluation/osu/k8s/container/build.sh` to build the benchmark container image. Note that this contains hard-coded paths to the patched libcxi and to a container registry, which must be adapted prior to reproduction on other systems.

Run the job file `evaluation/osu/k8s/mpi-job-volcano.yml`. After completion, run the `evaluation/osu/k8s/pv-inspector.yml` and run the command `kubectl -n stresstest cp pv-inspector:/pvc /path/to/storage` to extract the measurement data from the cluster to the host. This measures the baseline performance without the integration.

Repeat the same for file `evaluation/osu/k8s/mpi-job-volcano-vni.yml`. This measures the performance using our integration.

Move the output to folder `data/osu/container`.

Note that the files `mpi-job-volcano{-vni}.yml` contain hard-coded paths to the patched libcxi and a container registry holding the benchmark container image. Adapt these prior to reproduction on other systems.


#### Host (baseline)

The file `evaluation/osu/host/launcher_multi.sh` contains logic to perform MPI-based benchmarks using the OSU microbenchmark suite. Consult the `--help` output for documentation of the parameters.

Below are the parameters chosen for the benchmarks presented in the paper. Note that the paths are all relative to the system used and need to be adapted for reproduction on other systems.
```bash
bash launcher_multi.sh \
	--basedir $(pwd) \
	--mpirun /home/pfriese/build/ompi-5.0.7_ofi_cxi_build/bin/mpirun \
	--iterations 25 \
	--hostfile $(pwd)/hostfile \
	--mpi-args "-np 2 -x CXIP_SKIP_AMA_CHECK=true -x FI_CXI_LLRING_MODE=never -x FI_PROVIDER=cxi --mca pml cm --mca mtl ofi" \
	--binary /home/pfriese/build/osu-7.3-ompi5-cxi/c/mpi/pt2pt/standard/osu_bw

bash launcher_multi.sh \
	--basedir $(pwd) \
	--mpirun /home/pfriese/build/ompi-5.0.7_ofi_cxi_build/bin/mpirun \
	--iterations 25 \
	--hostfile $(pwd)/hostfile \
	--mpi-args "-np 2 -x CXIP_SKIP_AMA_CHECK=true -x FI_CXI_LLRING_MODE=never -x FI_PROVIDER=cxi --mca pml cm --mca mtl ofi" \
	--binary /home/pfriese/build/osu-7.3-ompi5-cxi/c/mpi/pt2pt/standard/osu_latency \
	--binary-args "-i 20000"
```

Move the output to folder `data/osu/host` if you did not specify it already in `--basedir`.

### Job Admission Overhead

Job admission overhead uses the `evaluation/job_admission/end-to-end/stresstest.sh` file. Consult the `--help` parameter for documentation of the arguments.

Below are the parameters used for the benchmarks presented in the paper.
Note that this script contains a hard-coded image path and `nodeSelector` label, which must be adapted for reproduction on other systems.

#### Spike

```bash
./stresstest.sh \
	--mode spike-test \
	--iterations 5 \
	--num-jobs 500

./stresstest.sh \
	--mode spike-test \
	--iterations 5 \
	--num-jobs 500 \
	--use-vni
```

#### Ramp

```bash
./stresstest.sh \
	--mode ramp-test \
	--ramp-step-wait 1 \
	--ramp-min 1 \
	--ramp-max 10 \
	--ramp-step-size 1 \
	--ramp-sustain 10 \
	--iterations 5

./stresstest.sh \
	--mode ramp-test \
	--ramp-step-wait 1 \
	--ramp-min 1 \
	--ramp-max 10 \
	--ramp-step-size 1 \
	--ramp-sustain 10 \
	--iterations 5 \
	--use-vni
```