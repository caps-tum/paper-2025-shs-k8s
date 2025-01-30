# Guide for HPE Slingshot 11 integration into Kubernetes


HPE Slingshot 11 is an HPC-focused high-performance network solution, providing RDMA capabilities. As a consequence, integration into container-based deployments using e.g. Kubernetes is not possible without further action.
This document describes the required further action.

Refer to `PROBLEM_STATEMENT.md` for background information.

Three components are necessary and described in this document:

1. Adjustments to CXI driver and userspace library `libcxi`
2. CXI CNI Plugin
3. VNI Service & Custom Resource for Kubernetes


The following instructions have been tested on an OpenSUSE Leap 15.5 Linux, kernel 5.14.21, libcxi version 1.5.5, podman version 4.9.5, k3s version v1.29.5, go version 1.22.6.

## CXI Driver and library adjustments

The patches in `patches/cxi-driver-libcxi` are responsible for adding the network-namespace member type `CXI_SVC_MEMBER_NET_NS` and the associated checking logic to the driver and libcxi.

## CXI CNI Plugin

The patches in `patches/cxi-cni` add the CXI CNI plugin to the CNI plugins repository (https://github.com/containernetworking/plugins). Check out the repository at [v1.6.2](https://github.com/containernetworking/plugins/tree/v1.6.2) and apply the patches.

Alternatively, clone the already-patched repository at: https://github.com/opencube-horizon/cxi-cni-plugin (git submodule `cxi-cni-plugin`).

Build the CXI CNI plugin by running the `build_linux.sh` file, which should generate a `cxi` binary in `$PWD/bin`. 

Adding this CNI plugin to a container runtime highly depends on the runtime in question. 


### K3s

K3s by default bundles flannel as its overlay container network. This disallows injecting a CNI. Therefore, k3s must be launched without default flannel using `flannel-backend: "none"` in the config file (or the `--flannel-backend none` parameter).
Next, re-add flannel:
- get the `kube-flannel.yaml` file from (https://github.com/flannel-io/flannel/blob/master/Documentation/kube-flannel.yml)
- add the `{ "type":"cxi" }` entry to the `cni-conf.json` entry in the `ConfigMap` entry of that yaml file.
- Since `/opt/cni/bin` is already mounted as a hostPath, no further action has to be taken in order to add the CXI CNI binary to the flannel containers.

Finally, apply the yaml file to the k3s cluster.

### Podman

For testing purposes, you can also add the CNI plugin to podman.

Add the `cxi` binary to `/opt/vni/bin/`. 
Add the following entry to /etc/containers/containers.conf`: 
```conf
[network]
network_backend="cni"
cni_plugin_dirs = [
 "/usr/local/libexec/cni",
 "/usr/libexec/cni",
 "/usr/local/lib/cni",
 "/usr/lib/cni",
 "/opt/cni/bin",
]
```

Create a new podman network using `sudo podman network create`.
Modify the network configuration file at `/etc/cni/net.d/cni-<name-of-network>.conflist` and add another entry to the `plugins` list:
```json
{ "type":"cxi" }
```

Note that the CXI CNI plugin must run as root / as a user priviledged to add/remove CXI services. Therefore we need to operate on root-visible files in `/etc`. Alternatively, `/root/.config/` can be used as well.


## VNI Service

The repository at https://github.com/opencube-horizon/vni-service or the git submodule `vni-service` contains the documentation and code for deploying the VNI service 