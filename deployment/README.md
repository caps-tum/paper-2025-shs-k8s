# Deplyoment

HPE Slingshot 11 is an HPC-focused high-performance network solution, providing RDMA capabilities. As a consequence, integration into container-based deployments using e.g. Kubernetes is not possible without further action.
This document describes the required further action.

Three components are necessary and described in this document:

1. Adjustments to CXI driver and userspace library `libcxi`
2. CXI CNI Plugin (including installation for k3s and podman)
3. VNI Service for Kubernetes


We also modify the network abstraction library Libfabric to support the modified `libcxi`.

Refer to [INSTALL.md](INSTALL.md) for details on installation.
