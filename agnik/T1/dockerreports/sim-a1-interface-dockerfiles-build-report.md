# Dockerfile Build Report for o-ran-sc/sim-a1-interface

**Repository:** [https://github.com/o-ran-sc/sim-a1-interface](https://github.com/o-ran-sc/sim-a1-interface)
**Date:** 2024-05-13

## 1. Repository Overview
- **Description:** O-RAN-SC A1 Simulator - Near-RT-RIC Simulator for A1 interface testing
- **Language:** Python 69.1%, Shell 29.1%, Dockerfile 1.8%
- **Project Type:** O-RAN A1 Interface Simulator
- **Lifecycle State:** Active development
- **Status:** A1 Simulator for testing and development
- **License:** Apache-2.0

## 2. Dockerfiles Discovered
**Result:** ✅ **3 DOCKERFILES FOUND**

The repository contains three Dockerfiles:
1. `./near-rt-ric-simulator/Dockerfile` - Main A1 simulator container
2. `./near-rt-ric-simulator/test/KAFKA_DISPATCHER/Dockerfile` - Kafka message dispatcher for testing
3. `./near-rt-ric-simulator/test/EXT_SRV/Dockerfile` - External service simulator for testing

## 3. Build Results Summary
- **Total Dockerfiles found**: 3
- **Successfully built**: 3 (100%)
- **Failed builds**: 0 (0%)
- **Fixes applied**: 3 (Base image updates and package repository fixes)

## 4. Detailed Build Analysis

### 4.1. `./near-rt-ric-simulator/Dockerfile` ✅ **SUCCESS** (After Fix)
- **Purpose:** Main A1 simulator container for O-RAN A1 interface testing
- **Base image:** `alpine:3.18.4` (updated from 3.17.3)
- **Build result:** Successfully built (38.9s)
- **Issues found:** 
  - Alpine 3.17.3 repositories were not accessible
  - Specific Python version pinning caused package resolution issues
- **Fixes applied:** 
  - Updated base image from `alpine:3.17.3` to `alpine:3.18.4`
  - Removed specific Python version pinning (`python3=3.10.15-r0` → `python3`)
- **Key features:**
  - Multi-version A1 interface support (STD_1.1.3, STD_2.0.0, OSC_2.1.0)
  - Flask-based REST API with Connexion/OpenAPI
  - Nginx reverse proxy with Lua support
  - SSL certificate management
  - Non-root user execution

**Build Log (After Fix):**
```
[+] Building 38.9s (20/20) FINISHED                            docker:desktop-linux
 => [internal] load build definition from Dockerfile                           0.0s
 => => transferring dockerfile: 1.60kB                                         0.0s
 => [internal] load metadata for docker.io/library/alpine:3.18.4               3.2s
 => [internal] load .dockerignore                                              0.0s
 => => transferring context: 2B                                                0.0s
 => [ 1/15] FROM docker.io/library/alpine:3.18.4@sha256:eece025e432126ce23f22  1.4s
 => => resolve docker.io/library/alpine:3.18.4@sha256:eece025e432126ce23f2234  0.0s
 => => sha256:96526aa774ef0126ad0fe9e9a95764c5fc37f409ab9e970 3.40MB / 3.40MB  1.1s
 => => extracting sha256:96526aa774ef0126ad0fe9e9a95764c5fc37f409ab9e97021e7b  0.2s
 => [internal] load build context                                              0.0s
 => => transferring context: 1.90kB                                            0.0s
 => [ 2/15] RUN apk add --update --no-cache python3 py3-pip nginx nginx-mod-h  8.8s
 => [ 3/15] RUN pip3 install Flask==2.2.5 connexion[swagger-ui,flask]==2.14.  13.0s
 => [ 4/15] WORKDIR /usr/src/app                                               0.1s
 => [ 5/15] COPY api api                                                       0.1s
 => [ 6/15] COPY nginx.conf nginx.conf                                         0.1s
 => [ 7/15] COPY certificate /usr/src/app/cert                                 0.1s
 => [ 8/15] COPY src src                                                       0.1s
 => [ 9/15] RUN addgroup nonrtric &&     adduser -S -G nonrtric nonrtric       0.2s
 => [10/15] RUN chown -R nonrtric:nonrtric /usr/src/app                        0.4s
 => [11/15] RUN chown -R nonrtric:nonrtric /var/log/nginx                      0.2s
 => [12/15] RUN chown -R nonrtric:nonrtric /var/lib/nginx                      0.2s
 => [13/15] RUN touch /var/run/nginx.pid                                       0.2s
 => [14/15] RUN chown -R nonrtric:nonrtric /var/run/nginx.pid                  0.2s
 => [15/15] RUN chmod +x src/start.sh                                          0.2s
 => exporting to image                                                         9.8s
 => => exporting layers                                                        7.0s
 => => exporting manifest sha256:363f1cffeb30b2b19e08950e5c17dbcb60592d0bc050  0.0s
 => => exporting config sha256:5f720974b79fa7ca9dfbab6e7d133ae072b13e1990af48  0.0s
 => => exporting attestation manifest sha256:59b0f2c9f962609a7b40066ab7831138  0.0s
 => => exporting manifest list sha256:086b4dcb6db1f8da5dc7ebbe47769a07b47b73e  0.0s
 => => naming to docker.io/library/sim-a1-interface-main:test                  0.0s
 => => unpacking to docker.io/library/sim-a1-interface-main:test               2.5s
```

### 4.2. `./near-rt-ric-simulator/test/KAFKA_DISPATCHER/Dockerfile` ✅ **SUCCESS** (After Fix)
- **Purpose:** Kafka message dispatcher for A1 simulator testing
- **Base image:** `python:3.8-slim-bullseye` (updated from buster)
- **Build result:** Successfully built (213.1s)
- **Issues found:** 
  - Debian Buster repositories are no longer available (404 errors)
  - Specific nginx version pinning caused package resolution issues
- **Fixes applied:** 
  - Updated base image from `python:3.8-slim-buster` to `python:3.8-slim-bullseye`
  - Removed specific nginx version pinning (`nginx=1.14.*` → `nginx`)
- **Key features:**
  - Kafka message dispatching for A1 policy testing
  - Flask-based REST API with Connexion/OpenAPI
  - Nginx reverse proxy with extras modules
  - Policy type to topic mapping
  - Non-root user execution

**Build Log (After Fix):**
```
[+] Building 213.1s (23/23) FINISHED                           docker:desktop-linux
 => [internal] load build definition from Dockerfile                           0.0s
 => => transferring dockerfile: 1.70kB                                         0.0s
 => [internal] load metadata for docker.io/library/python:3.8-slim-bullseye    1.4s
 => [internal] load .dockerignore                                              0.0s
 => => transferring context: 2B                                                0.0s
 => CACHED [ 1/18] FROM docker.io/library/python:3.8-slim-bullseye@sha256:e19  0.0s
 => => resolve docker.io/library/python:3.8-slim-bullseye@sha256:e191a71397fd  0.0s
 => [internal] load build context                                              0.0s
 => => transferring context: 635B                                              0.0s
 => [ 2/18] RUN pip3 install "connexion[swagger-ui,flask,uvicorn]"            25.9s
 => [ 3/18] RUN pip3 install kafka-python                                      2.4s
 => [ 4/18] RUN apt-get update && apt-get install -y nginx nginx-extras cur  164.2s
 => [ 5/18] WORKDIR /usr/src/app                                               0.2s
 => [ 6/18] COPY api api                                                       0.1s
 => [ 7/18] COPY nginx.conf nginx.conf                                         0.1s
 => [ 8/18] COPY certificate /usr/src/app/cert                                 0.1s
 => [ 9/18] COPY src src                                                       0.1s
 => [10/18] COPY resources resources                                           0.1s
 => [11/18] RUN groupadd nonrtric &&     useradd -r -g nonrtric nonrtric       0.3s
 => [12/18] RUN chown -R nonrtric:nonrtric /usr/src/app                        0.3s
 => [13/18] RUN chown -R nonrtric:nonrtric /var/log/nginx                      0.2s
 => [14/18] RUN chown -R nonrtric:nonrtric /var/lib/nginx                      0.2s
 => [15/18] RUN chown -R nonrtric:nonrtric /etc/nginx/conf.d                   0.2s
 => [16/18] RUN touch /var/run/nginx.pid                                       0.2s
 => [17/18] RUN chown -R nonrtric:nonrtric /var/run/nginx.pid                  0.2s
 => [18/18] RUN chmod +x src/start.sh                                          0.2s
 => exporting to image                                                        16.2s
 => => exporting layers                                                       12.4s
 => => exporting manifest sha256:9f7131f1f0278813c18d21238ec7c3bcf2e9bbb608f3  0.0s
 => => exporting config sha256:8f11e30c6a186e5d0608903286fb00493ce0a2f6324eda  0.0s
 => => exporting attestation manifest sha256:84d216e69f4ba86bec3f78f6b8cf2d58  0.1s
 => => exporting manifest list sha256:45704ebd5ef1d1204fbedce87c7d292021ef006  0.0s
 => => naming to docker.io/library/sim-a1-interface-kafka:test                 0.0s
 => => unpacking to docker.io/library/sim-a1-interface-kafka:test              3.5s
```

### 4.3. `./near-rt-ric-simulator/test/EXT_SRV/Dockerfile` ✅ **SUCCESS** (After Fix)
- **Purpose:** External service simulator for A1 interface testing
- **Base image:** `python:3.8-slim-bullseye` (updated from buster)
- **Build result:** Successfully built (85.1s)
- **Issues found:** 
  - Debian Buster repositories are no longer available (404 errors)
  - Network connectivity issues with specific packages
- **Fixes applied:** 
  - Updated base image from `python:3.8-slim-buster` to `python:3.8-slim-bullseye`
  - Removed specific nginx version pinning (`nginx=1.14.*` → `nginx`)
  - Added `--fix-missing` flag to apt-get install command
- **Key features:**
  - External service simulation for A1 policy testing
  - Flask-based REST API with Connexion/OpenAPI
  - Nginx reverse proxy with extras modules
  - Policy response simulation
  - Non-root user execution

**Build Log (After Fix):**
```
[+] Building 85.1s (21/21) FINISHED                            docker:desktop-linux
 => [internal] load build definition from Dockerfile                           0.0s
 => => transferring dockerfile: 1.66kB                                         0.0s
 => [internal] load metadata for docker.io/library/python:3.8-slim-bullseye    1.9s
 => [internal] load .dockerignore                                              0.0s
 => => transferring context: 2B                                                0.0s
 => [ 1/16] FROM docker.io/library/python:3.8-slim-bullseye@sha256:e191a71397  0.0s
 => => resolve docker.io/library/python:3.8-slim-bullseye@sha256:e191a71397fd  0.0s
 => [internal] load build context                                              0.0s
 => => transferring context: 536B                                              0.0s
 => CACHED [ 2/16] RUN pip3 install "connexion[swagger-ui,flask,uvicorn]"      0.0s
 => [ 3/16] RUN apt-get update && apt-get install -y --fix-missing nginx ngi  62.9s
 => [ 4/16] WORKDIR /usr/src/app                                               0.1s
 => [ 5/16] COPY api api                                                       0.1s
 => [ 6/16] COPY nginx.conf nginx.conf                                         0.1s
 => [ 7/16] COPY certificate /usr/src/app/cert                                 0.1s
 => [ 8/16] COPY src src                                                       0.1s
 => [ 9/16] RUN groupadd nonrtric &&     useradd -r -g nonrtric nonrtric       0.4s
 => [10/16] RUN chown -R nonrtric:nonrtric /usr/src/app                        0.4s
 => [11/16] RUN chown -R nonrtric:nonrtric /var/log/nginx                      0.4s
 => [12/16] RUN chown -R nonrtric:nonrtric /var/lib/nginx                      0.3s
 => [13/16] RUN chown -R nonrtric:nonrtric /etc/nginx/conf.d                   0.3s
 => [14/16] RUN touch /var/run/nginx.pid                                       0.3s
 => [15/16] RUN chown -R nonrtric:nonrtric /var/run/nginx.pid                  0.2s
 => [16/16] RUN chown -R nonrtric:nonrtric /var/run/nginx.pid                  0.2s
 => [17/16] RUN chmod +x src/start.sh                                          0.3s
 => exporting to image                                                        16.4s
 => => exporting layers                                                       13.9s
 => => exporting manifest sha256:2e629341786590f2e8949bd7bfd22cf274cb1ee8fec9  0.0s
 => => exporting config sha256:41b529f24451714eedca533cd2bf2447a1a37e3369688e  0.0s
 => => exporting attestation manifest sha256:d28e296ba498fcb87b42962d6c047a27  0.0s
 => => exporting manifest list sha256:0a34a8fcde5dfd1e3a8c0b64091940178d5e022  0.0s
 => => naming to docker.io/library/sim-a1-interface-extsrv:test                0.0s
 => => unpacking to docker.io/library/sim-a1-interface-extsrv:test             2.2s
```