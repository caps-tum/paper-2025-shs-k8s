# Install

The following instructions have been tested on an OpenSUSE Leap 15.5 Linux, kernel 5.14.21, libcxi version 1.5.5, podman version 4.9.5, k3s version v1.29.5, go version 1.22.6.


## CXI Driver and Library

Building the CXI kernel driver requires access to the full Slingshot software stack. Due to licensing concerns, the patches to these drivers can only be handed out upon request. 
Upstreaming these changes is planned.

## CXI CNI Plugin

Clone the CNI plugins repository at https://github.com/containernetworking/plugins. Tag v1.6.2. has been tested. Apply the patch in `patches/cni_plugin` to the repository.
Adjust file `plugins/cxi/cxi.go`, specifically the `CFLAGS` and `LDFLAGS` to point to the build directory of the patched libcxi library.

Run `go mod tidy` and then `go mod vendor`. Finally, run `build_linux.sh`, which should build the CXI plugin at `bin/cxi`. 

Move this binary to the folder of your CNI plugins. The exact location depends on the Kubernetes deployment and the used network software. For a default flannel, this is `/opt/cni/bin`.

### Install in K3s

K3s by default bundles flannel as its overlay container network. This disallows injecting a CNI. Therefore, k3s must be launched without default flannel using `flannel-backend: "none"` in the config file (or the `--flannel-backend none` parameter).
Next, re-add flannel:
- get the `kube-flannel.yaml` file from (https://github.com/flannel-io/flannel/blob/master/Documentation/kube-flannel.yml)
- add the `{ "type":"cxi" }` entry to the `cni-conf.json` entry in the `ConfigMap` entry of that yaml file.
- Since `/opt/cni/bin` is already mounted as a hostPath, no further action has to be taken in order to add the CXI CNI binary to the flannel containers.

Finally, apply the yaml file to the k3s cluster.

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


## Libfabric

Clone the libfabric repository at https://github.com/ofiwg/libfabric. Tag v2.1.0 has been tested. Apply the patch in `patches/libfabric` to the repository. Run `autogen.sh`. Configure the libfabric project to your needs and add the flag `--enable-cxi=true`. You might have do add explicit paths to several dependencies, such as `--with-json-c` or `--with-curl`. Build and install the project. The resulting libfabric library should now include the patched CXI stack. Verify that the cxi provider is available by running `fi_info -l`.
Note that this requires access to the libcxi library for building and a Slingshot NIC for testing.

## VNI Service

The repository at https://github.com/opencube-horizon/vni-service or the git submodule `vni-service` contains the documentation and code for deploying the VNI service 