#!/usr/bin/env bash

NAME="stresstest-osu"
TAG=1.3.3
buildah build \
  --compress \
  --layers \
  --squash \
  --tag "$NAME:$TAG"\
  --volume /opt/libcxi-netns/lib/libcxi.so.1.5.0:/usr/lib64/libcxi.so.1.5.0:ro \
  --volume /opt/libcxi-netns/lib/libcxi.so.1.5.0:/usr/lib64/libcxi.so.1:ro \
  --volume /opt/libcxi-netns/lib/libcxi.so.1.5.0:/usr/lib64/libcxi.so:ro \
  --volume /opt/libcxi-netns/lib/libcxi.a:/usr/lib64/libcxi.a:ro \
  --volume /opt/libcxi-netns/include/libcxi/libcxi.h:/usr/include/libcxi/libcxi.h:ro \
  --volume /opt/libcxi-netns/include/libcxi/uapi/misc/cxi.h:/usr/include/uapi/misc/cxi.h:ro \
  --volume /usr/include/cassini_cntr_block_defs.h:/usr/include/cassini_cntr_block_defs.h:ro \
  --volume /usr/include/cassini_cntr_block_values.h:/usr/include/cassini_cntr_block_values.h:ro \
  --volume /usr/include/cassini_cntr_defs.h:/usr/include/cassini_cntr_defs.h:ro \
  --volume /usr/include/cassini_cntr_desc.h:/usr/include/cassini_cntr_desc.h:ro \
  --volume /usr/include/cassini_cntr_sysfs_defs.h:/usr/include/cassini_cntr_sysfs_defs.h:ro \
  --volume /usr/include/cassini_csr_defaults.h:/usr/include/cassini_csr_defaults.h:ro \
  --volume /usr/include/cassini_error_defs.h:/usr/include/cassini_error_defs.h:ro \
  --volume /usr/include/cassini_telemetry.h:/usr/include/cassini_telemetry.h:ro \
  --volume /usr/include/cassini_user_defs.h:/usr/include/cassini_user_defs.h:ro \
  --volume /usr/include/libcassini.h:/usr/include/libcassini.h:ro \
  --volume /usr/include/cxi_prov_hw.h:/usr/include/cxi_prov_hw.h:ro \
  --file Dockerfile



  podman image push "localhost/$NAME:$TAG" "harbor.pt.horizon-opencube.eu/vni-system/$NAME:$TAG"