# Problem Statement

Slingshot assumes single-tenancy deployments, meaning strictly time-shared access with only one user per node at any time. In order to avoid users from accessing data from others without authorization, Slingshot provides isolation domains via Virtual Networks. Each Virtual Network, given an ID valled a VNI, isolates traffic, disallowing users within one VN to send packets to other VNs. Virtual Networks exist between different Cassini (CXI) NICs and the connecting Rosetta switches. Once a packet from one VN arrives at the CXI NIC, the firmware and driver is responsible for forwarding it to the right user via the respective buffer. 

This association of users to VNs is achieved using Services. A Slingshot service is implemented using the CXI driver and couples RDMA communication endpoints to VNIs. While VNIs provide secure communication between NICs, Services provide secure communication between users and one NIC.
A service consists of a set of valid VNIs and a set of authorized users. Users can only send packets through one VN if there exists a service with the corresponding VNI and where said users are authorized to use this service.

Services currently support authentication via Linux UIDs and GIDs. These checks do not extend to namespaces: If a service is restricted to e.g. the host root / host UID 0, and a container is executed with a user namespace, meaning the user inside the container as UID 0, then that user is authorized against that service. This effectively tears down the service-based security domain and voids the Slingshot isolation system for container-based deployments.

We mitigate this issue by adding a third authentication scheme using network namespace IDs. Each container (or sets of containers called pods) runs in one unique network namespace, which is uniquely identifiable. We add this ID to the set of authentication IDs of Slingshot Services. This way, users authenticate themselves not by their UID/GID (which can usually be arbitrarily chosen inside a container), but by running within one unique network namespace.
This approach solves a second problem: The container orchestrator Kubernetes, as used by OpenCUBE, runs all containers as one user. Even if namespaces are properly handled by the CXI driver, then this still implies that containers cannot be distinguished, since all run with the same effective/outer UID/GID. 

This approach implies that a new CXI service needs to be created for each running container/pod. This is achieved using a CXI CNI plugin, which is executed during container creation and subsequent tear-down and which creates and deletes the corresponding CXI service.

In order for two containers running on two nodes to be able to communicate, both containers need to have access to services which share a VNI. If a set of containers, for example as part of a job, is launched, then each CXI CNI plugin must create a service containing the same VNI. 
To avoid race-conditions, we add the concept of VNIs to Kubernetes using custom resources. During the creation of a Kubernetes Job (/deployment/replica-set/...), annotated to require a shared VNI, a custom controller will generate a new, unique VNI, create a Custom Resource, and attach this VNI CR to each to-be-created container.
The CXI CNI plugin running on each involved node will then read the VNI from the CR attached to the container and use this VNI to create the new service.
During tear-down, the custom resource controller will delete the VNI CR and recycle it.


## Terminology

- RDMA: Remote Direct Memory Access
- CXI: Cassini 11 (Slingshot NIC)
- Rosetta: Slingshot Switch
- VNI: Virtual Network ID
- SVC: Service
- CNI: Container Network Interface
- CRD: Custom Resource Definition