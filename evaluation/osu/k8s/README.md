This dockerfile builds a container with a patched libfabric 2.1.0, an Open MPI 5.0.7, and an OSU Microbenchmark Suite.

Build requires adding libcxi and cassini headers. Build for example with `bash build.sh`.

The data will be written to a persistent volume. Use the `pv-inspector.yaml` for access:

```bash
kubectl apply -f pv-inspector.yaml
kubectl -n stresstest cp pv-inspector:/pvc /path/to/storage/on/host
```