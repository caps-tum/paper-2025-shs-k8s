# Install

The following instructions have been tested on an OpenSUSE Leap 15.5 Linux, kernel 5.14.21, libcxi version 1.5.5, podman version 4.9.5, k3s version v1.29.5, go version 1.22.6.
We assume an already-running k3s system.

## CXI Driver and Library

Building the CXI kernel driver requires access to the full Slingshot software stack. The patches to `libcxi` and the Slingshot Cassini driver are attached under `patches/{libcxi,shs-cxi-driver}`, respectively. Consult HPE documentation for how to install these patches based on the Slingshot hardware you may have.

Upstreaming these patches is planned.

## CXI CNI Plugin

Clone the CNI plugins repository at https://github.com/containernetworking/plugins. Tag v1.6.2. has been tested. Apply the patch in `patches/cni_plugin` to the repository.
Adjust file `plugins/cxi/cxi.go`, specifically the `CFLAGS` and `LDFLAGS` to point to the build directory of the patched libcxi library.

Run `go mod tidy` and then `go mod vendor`. Finally, run `build_linux.sh`, which should build the CXI plugin at `bin/cxi`. 

Move this binary to the folder of your CNI plugins. The exact location depends on the Kubernetes deployment and the used network software. For a default flannel, this is `/opt/cni/bin`.

The currrent version (as of 2025-10-10) fetches information on pods and VNI CRs from the cluster via the kubelet API server. The connection is established via a K8s client. The configuration file for that client is read from a file at `/etc/rancher/k3s/k3s.yaml`. This file is basically your `~/.kube/config` file. Make sure you create a file at that location _on all nodes_ and make sure that the permissions of the client certificates in that file allow the CXI CNI plugin to read VNI CRs!

### Install in K3s via Flannel

(This variant is used in the paper.)

K3s by default bundles flannel as its overlay container network. This disallows injecting a CNI. 
Therefore, k3s must be launched without default flannel using `flannel-backend: "none"` in the config file (or the `--flannel-backend none` parameter).
> Note: You will need to wipe & re-initialise the k3s cluster if you have initialised it with the bundled flannel overlay network.
> K3s provides a [killall](https://docs.k3s.io/upgrades/killall) script for this purpose. 

Next, re-add flannel:
- get the `kube-flannel.yaml` file from (https://github.com/flannel-io/flannel/blob/master/Documentation/kube-flannel.yml)
- add the `{ "type":"cxi" }` entry to the `cni-conf.json` setting in the `ConfigMap` entry of that yaml file, specifically to the `plugins` array.
- Since `/opt/cni/bin` is already mounted as a hostPath, no further action has to be taken in order to add the CXI CNI binary to the flannel containers.

Finally, apply the updated yaml file to the k3s cluster. This should add flannel to the k3s cluster and add the CXI CNI binary as a dependency to all overlay networks.

### Install via Cilium

Cilium exposes the setting `cni.customConf` during installation. If set to true, the CNI configuration file at `cni.confPath` (default: `/etc/cni/net.d`) will not be automatically generated. One approach for deploying the CXI CNI plugin is to deploy Cilium using default settings, letting it generate a CNI configuration e.g. at `/etc/cni/net.d/05-cilium.conflist`. Then uninstall cilium, modify the configuration file by adding `{ "type": "cxi" }` as a plugin, and then reinstalling it with the option `cni.customConf=true`. Note that the `cxi` CNI plugin binary must be located at the folder specified at `cni.binPath`. Also note that the whole path must be owned by `root:root`!

The remaining installation process is identical to the Cilium process. 

### Install in Podman

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

The code at https://github.com/opencube-horizon/vni-service contains the documentation and code for deploying the VNI service.
Alternatively, you can use the git submodule at `repositories/vni-service`. Make sure to run `git pull --recurse-submodules` to properly pull the submodule.

## Libfabric

Clone the libfabric repository at https://github.com/ofiwg/libfabric. Tag v2.1.0 has been tested. Apply the patch in `patches/libfabric` to the repository. Run `autogen.sh`. Configure the libfabric project to your needs and add the flag `--enable-cxi=true`. You might have do add explicit paths to several dependencies, such as `--with-json-c` or `--with-curl`. Build and install the project. The resulting libfabric library should now include the patched CXI stack. Verify that the cxi provider is available by running `fi_info -l`.
Note that this requires access to the libcxi library for building and a Slingshot NIC for testing.
