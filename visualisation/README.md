# Visualisation

This directory contains all files for reproducing all data-related figures in the paper.

The associated Python scripts have been developed and run on a Linux machine using Python 3.13.
The package requirements are listed in `requirements.txt`. Please install these, ideally in a virtual environment, prior to executing the scripts.

The source file for all figures in the paper is:

- Figure 1: `figures/other/cxi-vni-svc.pdf`
- Figure 2: `figures/other/shs-stack.pdf`
- Figure 3: `figures/other/vni-service.pdf`
- Figure 4: `figures/other/vni-models.pdf`
- Figure 5: `figures/osu/figures/raw_osu_bw.pdf`
- Figure 6: `figures/osu/figures/osu_bw.pdf`
- Figure 7: `figures/osu/figures/raw_osu_latency.pdf`
- Figure 8: `figures/osu/figures/osu_latency.pdf`
- Figure 9: `figures/ramp/active_jobs.pdf`
- Figure 10: `figures/ramp/job_delay_batch.pdf`
- Figure 11: `figures/spike/active_jobs.pdf`
- Figure 12: `figures/{spike,ramp}/job_delay.pdf`


Based on the evaluation data stored in `data/`, run the following commands to reproduce the Figures 5-12:

```bash
PYTHONPATH=$(pwd) python3 visualisation/main.py
```

Please make sure to run this from the root directory and to set the PYTHONPATH variable.

Figures 1-4 have been custom-made and are not automatically generated.