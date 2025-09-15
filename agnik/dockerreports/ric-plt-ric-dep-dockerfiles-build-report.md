# Dockerfile Build Report for o-ran-sc/ric-plt-ric-dep

**Repository:** [https://github.com/o-ran-sc/ric-plt-ric-dep](https://github.com/o-ran-sc/ric-plt-ric-dep)
**Date:** 2024-05-13

## 1. Repository Overview
- **Description:** RIC Platform RIC Deployment - RIC platform deployment and management tools
- **Language:** Go 43.9%, Smarty 30.5%, Mustache 17.6%, Shell 5.6%, Makefile 1.9%, Dockerfile 0.5%
- **Project Type:** RIC platform deployment and Kubernetes operator
- **Lifecycle State:** Active development
- **Status:** Mirror of upstream Gerrit repo

## 2. Dockerfiles Discovered
**Result:** ✅ **3 DOCKERFILES FOUND**

The repository contains three Dockerfiles:
1. `./ci/Dockerfile` - CI/CD testing environment
2. `./ric-common/Initcontainer/docker/Dockerfile` - RIC platform init container
3. `./depRicKubernetesOperator/Dockerfile` - Kubernetes operator for RIC deployment

## 3. Build Results Summary
- **Total Dockerfiles found**: 3
- **Successfully built**: 2 (67%)
- **Failed builds**: 1 (33%)
- **Fixes applied**: 1 (Kubernetes operator)

## 4. Detailed Build Analysis

### 4.1. `./ci/Dockerfile` ❌ **FAILED**
- **Purpose:** CI/CD testing environment for RIC platform validation
- **Base image:** `ubuntu:18.04`
- **Build result:** Failed due to missing dependencies
- **Issues found:** 
  - Missing git dependency
  - Missing wget dependency
  - Missing chartmuseum dependency
  - Script execution path issues
- **Fixes applied:** 
  - Added git and wget to package installation
  - Fixed COPY path from `.` to `..`
  - Added chartmuseum installation (attempted but failed due to version issues)
- **Status:** Partially fixed but still failing due to chartmuseum dependency issues

**Build Log (Final Attempt):**
```
[+] Building 73.0s (10/13)                                     docker:desktop-linux
 => [internal] load build definition from Dockerfile                           0.0s
 => => transferring dockerfile: 1.44kB                                         0.0s
 => [internal] load metadata for docker.io/library/ubuntu:18.04                0.0s
 => [internal] load .dockerignore                                              0.0s
 => => transferring context: 2B                                                0.0s
 => CACHED [1/9] FROM docker.io/library/ubuntu:18.04@sha256:152dc042452c49600  0.0s
 => resolve docker.io/library/ubuntu:18.04@sha256:152dc042452c496007f07ca9  0.0s
 => [internal] load build context                                              0.1s
 => => transferring context: 68.00kB                                           0.1s
 => CACHED [2/9] RUN apt-get update && apt-get -y install curl git wget        0.0s
 => CACHED [3/9] RUN curl --silent --show-error --connect-timeout 10 --retry   0.0s
 => CACHED [4/9] RUN bash get_helm.sh                                          0.0s
 => CACHED [5/9] RUN helm init -c --skip-repos                                 0.0s
 => ERROR [6/9] RUN apt-get install -y golang-go &&     go install github.co  72.8s
------
 > [6/9] RUN apt-get install -y golang-go &&     go install github.com/helm/chartmuseum/cmd/chartmuseum@latest &&     mv /root/go/bin/chartmuseum /usr/local/bin/:      
0.171 Reading package lists...
...
71.94 can't load package: package github.com/helm/chartmuseum/cmd/chartmuseum@latest: cannot find package "github.com/helm/chartmuseum/cmd/chartmuseum@latest" in any of:                                                                                   
71.94   /usr/lib/go-1.10/src/github.com/helm/chartmuseum/cmd/chartmuseum@latest (from $GOROOT)                                                                          
71.94   /root/go/src/github.com/1.10/src/github.com/helm/chartmuseum/cmd/chartmuseum@latest (from $GOPATH)                                                                          
------
```

### 4.2. `./ric-common/Initcontainer/docker/Dockerfile` ✅ **SUCCESS**
- **Purpose:** Generic init container for RIC Platform components
- **Base image:** `alpine:latest`
- **Build result:** Successfully built (13.9s)
- **Issues found:** None
- **Fixes applied:** None
- **Key features:**
  - Lightweight Alpine-based init container
  - Includes kubectl for Kubernetes operations
  - Supports RIC platform initialization
  - Includes iproute2 and openssl utilities

**Build Log:**
```
[+] Building 13.9s (13/13) FINISHED                            docker:desktop-linux
 => [internal] load build definition from Dockerfile                           0.0s
 => => transferring dockerfile: 1.33kB                                         0.0s
 => WARN: MaintainerDeprecated: Maintainer instruction is deprecated in favor  0.0s
 => [internal] load metadata for docker.io/library/alpine:latest               3.2s
 => [internal] load .dockerignore                                              0.1s
 => => transferring context: 2B                                                0.0s
 => CACHED [1/7] FROM docker.io/library/alpine:latest@sha256:4bcff63911fcb444  0.1s
 => resolve docker.io/library/alpine:latest@sha256:4bcff63911fcb4448bd4fda  0.1s
 => CACHED [5/7] ADD https://storage.googleapis.com/kubernetes-release/releas  0.4s
 => [internal] load build context                                              0.1s
 => => transferring context: 832B                                              0.2s
 => [2/7] RUN apk update                                                       2.3s
 => [3/7] RUN apk add iproute2                                                 1.5s
 => [4/7] RUN apk add openssl                                                  1.6s
 => [5/7] ADD https://storage.googleapis.com/kubernetes-release/release/v1.14  0.3s
 => [6/7] RUN chmod +x /bin/kubectl                                            0.3s
 => [7/7] COPY bin/ricplt-init.sh /ricplt-init.sh                              0.1s
 => exporting to image                                                         4.1s
 => => exporting layers                                                        3.3s
 => => exporting manifest sha256:810b011b0b551fc064f5601dfaf30e8f0bd77e3d45ff  0.0s
 => => exporting config sha256:7619e041d910852a967db04758cc08e38563f1ada32f76  0.0s
 => => exporting attestation manifest sha256:786b10361b2906a0986b3a089b6d21c1  0.0s
 => => exporting manifest list sha256:ed8e8724ff321b36e160944c7b221a6de995687  0.0s
 => => naming to docker.io/library/ric-plt-ric-dep-initcontainer:test          0.0s
 => => unpacking to docker.io/library/ric-plt-ric-dep-initcontainer:test       0.6s

 2 warnings found (use docker --debug to expand):
 - MaintainerDeprecated: Maintainer instruction is deprecated in favor of using label (line 19)                                                                         
 - JSONArgsRecommended: JSON arguments recommended for CMD to prevent unintended behavior related to OS signals (line 36)                                               
```

### 4.3. `./depRicKubernetesOperator/Dockerfile` ✅ **SUCCESS** (After Fixes)
- **Purpose:** Kubernetes operator for RIC deployment management
- **Base image:** `golang:1.20` (builder), `gcr.io/distroless/static:nonroot` (runtime)
- **Build result:** Successfully built (64.6s)
- **Issues found:** Multiple Go compilation errors
- **Fixes applied:** 
  - Added missing imports for Kubernetes API packages
  - Added missing helper functions (boolPtr, int64Ptr, stringPtr, getDataForSecret)
  - Cleaned up unused imports
  - Fixed resource import for StatefulSet
- **Key features:**
  - Multi-stage build with Go 1.20
  - Distroless runtime image for security
  - Kubernetes operator for RIC platform management
  - Comprehensive RIC platform resource definitions

**Build Log (After Fixes):**
```
[+] Building 64.6s (17/17) FINISHED                            docker:desktop-linux
 => [internal] load build definition from Dockerfile                           0.0s
 => => transferring dockerfile: 1.35kB                                         0.0s
 => WARN: FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 2  0.0s
 => [internal] load metadata for gcr.io/distroless/static:nonroot              0.8s
 => [internal] load metadata for docker.io/library/golang:1.20                 1.0s
 => [internal] load .dockerignore                                              0.0s
 => => transferring context: 160B                                              0.0s
 => [builder 1/9] FROM docker.io/library/golang:1.20@sha256:8f9af7094d0cb27cc  0.1s
 => resolve docker.io/library/golang:1.20@sha256:8f9af7094d0cb27cc783c697a  0.0s
 => [internal] load build context                                              0.0s
 => => transferring context: 55.22kB                                           0.0s
 => CACHED [stage-1 1/3] FROM gcr.io/distroless/static:nonroot@sha256:e8a4044  0.1s
 => resolve gcr.io/distroless/static:nonroot@sha256:e8a4044e0b4ae4257efa45  0.1s
 => CACHED [builder 2/9] WORKDIR /workspace                                    0.0s
 => CACHED [builder 3/9] COPY go.mod go.mod                                    0.0s
 => CACHED [builder 4/9] COPY go.sum go.sum                                    0.0s
 => CACHED [builder 5/9] RUN go mod download                                   0.0s
 => CACHED [builder 6/9] COPY cmd/main.go cmd/main.go                          0.0s
 => CACHED [builder 7/9] COPY api/ api/                                        0.0s
 => [builder 8/9] COPY internal/controller/ internal/controller/               0.2s
 => [builder 9/9] RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -o m  57.5s
 => [stage-1 2/3] COPY --from=builder /workspace/manager .                     1.1s
 => exporting to image                                                         4.3s
 => => exporting layers                                                        3.5s
 => => exporting manifest sha256:42b1cb20d2571d7a5fe96cc80228a9c246fd16031f25  0.0s
 => => exporting config sha256:d30fdfc692959b06a025e52becb7a6dabfba3d950d3c50  0.0s
 => => exporting attestation manifest sha256:edd6cd7f68f624e7a9d6bff5e2fabb5b  0.1s
 => => exporting manifest list sha256:fcb98401086b1aae22520c7dd0d7cb265d2bf9b  0.0s
 => => naming to docker.io/library/ric-plt-ric-dep-operator:test               0.0s
 => => unpacking to docker.io/library/ric-plt-ric-dep-operator:test            0.6s

 1 warning found (use docker --debug to expand):
 - FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 2)
```