.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. SPDX-License-Identifier: CC-BY-4.0
.. ===============LICENSE_START=======================================================
.. Copyright (C) 2019-2020 AT&T Intellectual Property
.. ===================================================================================
.. This documentation file is distributed under the Creative Commons Attribution
.. 4.0 International License (the "License"); you may not use this file except in
.. compliance with the License.  You may obtain a copy of the License at
..
.. http://creativecommons.org/licenses/by/4.0
..
.. This file is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
.. ===============LICENSE_END=========================================================


Getting and Preparing Deployment Scripts
----------------------------------------

Clone the ric-plt/dep git repository that has deployment scripts and support files on the target VM.

.. code:: bash

  git clone https://github.com/o-ran-sc/ric-plt-ric-dep.git
  cd ric-plt-ric-dep

Deploying the Infrastructure and Platform Groups
------------------------------------------------

The legacy ``ci/`` and ``new-installer/`` trees were removed. A clean installation on Ubuntu 22.04 now
uses ``kubeadm`` directly, followed by the existing Helm helper scripts. The exact sequence used for the
latest validation run is shown below.

1. **Install prerequisites (containerd, kubeadm, kubelet, kubectl, CNI)**

   .. code:: bash

      export DEBIAN_FRONTEND=noninteractive
      sudo apt-get update
      sudo apt-get install -y apt-transport-https ca-certificates curl gpg lsb-release containerd
      sudo mkdir -p /etc/apt/keyrings
      curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | \
        sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
      printf "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] \
https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /\n" | \
        sudo tee /etc/apt/sources.list.d/kubernetes.list >/dev/null
      sudo apt-get update
      sudo apt-get install -y kubelet kubeadm kubectl kubernetes-cni
      sudo apt-mark hold kubelet kubeadm kubectl

2. **Configure containerd to use systemd cgroups and enable services**

   .. code:: bash

      sudo mkdir -p /etc/containerd
      containerd config default | sudo tee /etc/containerd/config.toml >/dev/null
      sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
      sudo systemctl restart containerd
      sudo systemctl enable containerd kubelet

3. **Initialize the control plane and configure kubectl**

   .. code:: bash

      sudo kubeadm init --pod-network-cidr=10.244.0.0/16
      mkdir -p $HOME/.kube
      sudo cp /etc/kubernetes/admin.conf $HOME/.kube/config
      sudo chown $(id -u):$(id -g) $HOME/.kube/config

4. **Install Flannel CNI and allow workloads on the control-plane node (single-node labs)**

   .. code:: bash

      KUBECONFIG=$HOME/.kube/config kubectl apply --validate=false \
        -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
      KUBECONFIG=$HOME/.kube/config kubectl taint nodes --all node-role.kubernetes.io/control-plane:NoSchedule-

5. **Install Helm helper and ric-common templates**

   .. code:: bash

      cd ric-dep/bin
      ./install_common_templates_to_helm.sh

After these steps ``kubectl get nodes`` should show the control-plane node in ``Ready`` state and you can
proceed to recipe customization.


Modify the deployment recipe
----------------------------

The repository now ships a minimal, curated set of recipes in ``RECIPE_EXAMPLE/``:

* ``example_recipe_latest_stable.yaml`` – symlink that always points to the newest stable recipe
* ``example_recipe_oran_j_release.yaml`` – O-RAN J release
* ``example_recipe_oran_k_release.yaml`` – O-RAN K release
* ``example_recipe_oran_l_release.yaml`` – O-RAN L release

Copy the file that best matches your target release and edit it in place. At a minimum update the
``ricip`` and ``auxip`` fields so that they match the host IP of the deployment VM.

.. code:: bash

  extsvcplt:
    ricip: ""
    auxip: ""

- Deployment scripts support both helm v2 and v3. The deployment script will determine the helm version installed in cluster during the deployment.
- To specify which version of the RIC platform components will be deployed, update the RIC platform component container tags in their corresponding section.
- You can specify which docker registry will be used for each component. If the docker registry requires login credential, you can add the credential in the following section. Please note that the installation suite has already included credentials for O-RAN Linux Foundation docker registries. Please do not create duplicate entries.

.. code:: bash

  docker-credential:
    enabled: true
    credential:
      SOME_KEY_NAME:
        registry: ""
        credential:
          user: ""
          password: ""
          email: ""

For more advanced recipe configuration options, please refer to the recipe configuration guideline.

Installing the RIC
------------------

After updating the recipe you can deploy the RIC with the command below. Use the latest stable recipe
or select the release-specific file you edited earlier.

.. code:: bash

  cd ric-dep/bin
  ./install -f ../RECIPE_EXAMPLE/example_recipe_latest_stable.yaml


Checking the Deployment Status
------------------------------

After running ``./install -f <recipe>`` and waiting a few minutes, a healthy system looks like:

.. code::

  $ helm list -n ricplt
  NAME                 	REVISION	UPDATED                        	STATUS  	CHART            	APP VERSION	NAMESPACE
  r4-infrastructure    	1       	Wed Nov 26 08:50:49 2025       	deployed	infrastructure-4.0	latest     	ricplt
  r4-dbaas             	1       	Wed Nov 26 08:51:03 2025       	deployed	dbaas-4.0       	latest     	ricplt
  r4-appmgr            	1       	Wed Nov 26 08:51:11 2025       	deployed	appmgr-4.0      	latest     	ricplt
  ... (remaining components omitted for brevity)

  $ kubectl get pods -n ricplt
  deployment-ricplt-a1mediator-64fd4bf64-5c2cf                 1/1   Running
  deployment-ricplt-alarmmanager-7d47d8f4d4-zbgj6              1/1   Running
  deployment-ricplt-appmgr-79848f94c-bccmw                     1/1   Running
  deployment-ricplt-e2mgr-856f655b4-bksfx                      1/1   Running
  deployment-ricplt-e2term-alpha-d5fd5d9c6-4k28s               1/1   Running
  deployment-ricplt-o1mediator-76c4646878-wk9dw                1/1   Running
  deployment-ricplt-rtmgr-6556c5bc7b-9wx78                     1/1   Running
  deployment-ricplt-submgr-66485ccc6c-cst45                    1/1   Running
  deployment-ricplt-vespamgr-786666549b-cdj8z                  1/1   Running
  r4-infrastructure-kong-5986fc7965-v2qkw                      2/2   Running
  r4-infrastructure-prometheus-alertmanager-64f9876d6d-29s2w   2/2   Running
  r4-infrastructure-prometheus-server-bcc8cc897-l2sfv          1/1   Running
  statefulset-ricplt-dbaas-server-0                            1/1   Running

  $ kubectl get pods -n ricinfra
  deployment-tiller-ricxapp-676dfd8664-9fbkj   1/1   Running
  tiller-secret-generator-jns95                0/1   Completed

Checking Container Health
-------------------------

Check the health of the application manager platform component by querying it
via the ingress controller using the following command.

.. code:: bash

  % curl -v http://localhost:32080/appmgr/ric/v1/health/ready

The output should look as follows.

.. code::

  *   Trying 10.0.2.100...
  * TCP_NODELAY set
  * Connected to 10.0.2.100 (10.0.2.100) port 32080 (#0)
  > GET /appmgr/ric/v1/health/ready HTTP/1.1
  > Host: 10.0.2.100:32080
  > User-Agent: curl/7.58.0
  > Accept: */*
  >
  < HTTP/1.1 200 OK
  < Content-Type: application/json
  < Content-Length: 0
  < Connection: keep-alive
  < Date: Wed, 22 Jan 2020 20:55:39 GMT
  < X-Kong-Upstream-Latency: 0
  < X-Kong-Proxy-Latency: 2
  < Via: kong/1.3.1
  <
  * Connection #0 to host 10.0.2.100 left intact


Undeploying the Infrastructure and Platform Groups
--------------------------------------------------

To undeploy all the containers, perform the following steps in a root shell
within the it-dep repository.

.. code:: bash

  # cd bin
  # ./uninstall

Results similar to below indicate a complete and successful cleanup.

.. code::

  # ./undeploy-ric-platform
  Undeploying RIC platform components [appmgr rtmgr dbaas1 e2mgr e2term a1mediator submgr vespamgr rsm jaegeradapter infrastructure]
  release "r3-appmgr" deleted
  release "r3-rtmgr" deleted
  release "r3-dbaas1" deleted
  release "r3-e2mgr" deleted
  release "r3-e2term" deleted
  release "r3-a1mediator" deleted
  release "r3-submgr" deleted
  release "r3-vespamgr" deleted
  release "r3-rsm" deleted
  release "r3-jaegeradapter" deleted
  release "r3-infrastructure" deleted
  configmap "ricplt-recipe" deleted
  namespace "ricxapp" deleted
  namespace "ricinfra" deleted
  namespace "ricplt" deleted


Restarting the VM
-----------------

After a reboot of the VM, and a suitable delay for initialization,
all the containers should be running again as shown above.

RIC Applications
----------------

.. include:: installation-xapps.rst

OPTIONALLY use Redis Cluster (instead of Redis standalone)
----------------------------------------------------------

.. include:: installation-rediscluster.rst
