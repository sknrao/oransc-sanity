# Dockerfile Build Report for o-ran-sc/ric-plt-xapp-frame

**Repository:** [https://github.com/o-ran-sc/ric-plt-xapp-frame](https://github.com/o-ran-sc/ric-plt-xapp-frame)
**Date:** 2024-05-13

## 1. Repository Overview
- **Description:** XAPP-FRAME - A simple framework for rapid development of RIC xapps
- **Language:** Go 95.8%, Makefile 2.8%, Dockerfile 1.4%
- **Project Type:** RIC xApp development framework
- **Lifecycle State:** Active development
- **Status:** Mirror of upstream Gerrit repo

## 2. Dockerfiles Discovered
**Result:** ✅ **2 DOCKERFILES FOUND**

The repository contains two Dockerfiles:
1. `./ci/Dockerfile` - CI/CD testing environment for xApp framework
2. `./examples/build/Dockerfile` - Example xApp container build

## 3. Build Results Summary
- **Total Dockerfiles found**: 2
- **Successfully built**: 1 (50%)
- **Failed builds**: 1 (50%)
- **Fixes applied**: 1 (CI Dockerfile context fix)

## 4. Detailed Build Analysis

### 4.1. `./ci/Dockerfile` ✅ **SUCCESS** (After Fix)
- **Purpose:** CI/CD testing environment for xApp framework development
- **Base image:** `nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubuntu20-c-go:1.1.0`
- **Build result:** Successfully built (469.0s)
- **Issues found:** 
  - Initial build failed due to wrong build context (trying to copy go.mod/go.sum from ci/ directory)
- **Fixes applied:** 
  - Built from parent directory to provide correct context for go.mod/go.sum files
- **Key features:**
  - Multi-stage build with Ubuntu 20.04 and Go development environment
  - RMR (RIC Message Routing) library installation
  - Comprehensive build tools and utilities
  - Go module dependency management
  - Automated testing and formatting

**Build Log (After Fix):**
```
[+] Building 469.0s (20/20) FINISHED                           docker:desktop-linux
 => [internal] load build definition from Dockerfile                           0.1s
 => => transferring dockerfile: 2.63kB                                         0.0s
 => [internal] load metadata for nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubun  0.3s
 => [internal] load .dockerignore                                              0.1s
 => => transferring context: 55B                                               0.0s
 => [xapp-base 1/8] FROM nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubuntu20-c  281.0s
 => => resolve nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubuntu20-c-go:1.1.0@sh  0.0s
 => => sha256:b6bb5771e098c60fe00d59a9695463fd8bd7d20fae07c7f 8.47MB / 8.47MB  6.5s
 => => sha256:7fe92f986395a2f764cdc8004cf8ccb3f39af358b86d 42.84MB / 42.84MB  40.2s
 => => sha256:a4fc8b85b2bf994c43a6e5fbdbfc550133e0dd38655a 27.94MB / 27.94MB  26.0s
 => => sha256:e018b0ccca623a30b374a2456d7f918faa29e8cd4 141.86MB / 141.86MB  103.6s
 => => sha256:b883034e48072455c0524f01f0022e1da45a328de0 134.96MB / 134.96MB  65.6s
 => => sha256:4ea9066545e11055204cd3be7413128b91385b9a82 129.05MB / 129.05MB  32.2s
 => => sha256:ae28b6acf6f1d0d15609df8d5e283f2e7ccf35d2ca2fda9be3a 144B / 144B  0.3s
 => => sha256:54cd83c3e1c238b5aea2fa3b9c482162e18d3619a 337.65MB / 337.65MB  197.6s
 => => sha256:eaead16dc43bb8811d4ff450935d607f9ba4baffda4fc 28.58MB / 28.58MB  8.2s
 => => extracting sha256:eaead16dc43bb8811d4ff450935d607f9ba4baffda4fc110cc40  1.0s
 => => extracting sha256:54cd83c3e1c238b5aea2fa3b9c482162e18d3619af649fca4fe  13.4s
 => => extracting sha256:ae28b6acf6f1d0d15609df8d5e283f2e7ccf35d2ca2fda9be3a3  0.0s
 => => extracting sha256:4ea9066545e11055204cd3be7413128b91385b9a8234c5426e2c  7.1s
 => => extracting sha256:b883034e48072455c0524f01f0022e1da45a328de0545b7a435e  6.8s
 => => extracting sha256:e018b0ccca623a30b374a2456d7f918faa29e8cd45c376ee63c  11.6s
 => => extracting sha256:a4fc8b85b2bf994c43a6e5fbdbfc550133e0dd38655a9c3e65c0  0.9s
 => => extracting sha256:7fe92f986395a2f764cdc8004cf8ccb3f39af358b86d40ea007a  0.8s
 => => extracting sha256:b6bb5771e098c60fe00d59a9695463fd8bd7d20fae07c7f8a692  1.4s
 => => [internal] load build context                                              0.4s
 => => transferring context: 1.32MB                                            0.1s
 => [xapp-base 2/8] RUN apt-get update -y     &&apt-get install -y     apt-u  64.0s
 => [xapp-base 3/8] RUN curl -s https://packagecloud.io/install/repositories  24.1s
 => [xapp-base 4/8] RUN wget --content-disposition https://packagecloud.io/o-  3.1s
 => [xapp-base 5/8] RUN wget --content-disposition https://packagecloud.io/o-  1.9s
 => [xapp-base 6/8] RUN rm -f rmr_4.9.4_amd64.deb rmr-dev_4.9.4_amd64.deb      0.1s
 => [xapp-base 7/8] RUN ldconfig                                               0.2s
 => [xapp-base-testbuild 1/8] RUN mkdir -p /ws                                 0.2s
 => [xapp-base-testbuild 2/8] WORKDIR /ws                                      0.2s
 => [xapp-base-testbuild 3/8] COPY go.mod /ws                                  0.2s
 => [xapp-base-testbuild 4/8] COPY go.sum /ws                                  0.2s
 => [xapp-base-testbuild 5/8] RUN go mod download                             15.3s
 => [xapp-base-testbuild 6/8] COPY . /ws                                       0.3s
 => [xapp-base-testbuild 7/8] RUN make -C /ws go-build                        53.7s
 => [xapp-base-testbuild 8/8] RUN make -C /ws go-test-fmt                      0.4s
 => exporting to image                                                        22.8s
 => => exporting layers                                                       15.7s
 => => exporting manifest sha256:09fffbee19550daedec2877de456e98832d26417d747  0.0s
 => => exporting config sha256:d03ad59782d7beafb15fc2690755994491690fa616e236  0.0s
 => => exporting attestation manifest sha256:6b894d8967e263285e0fbd4be105c016  0.1s
 => => exporting manifest list sha256:8c879d218625a69161e624edcc9af1def12e080  0.0s
 => => naming to docker.io/library/ric-plt-xapp-frame-ci:test                  0.0s
 => => unpacking to docker.io/library/ric-plt-xapp-frame-ci:test               6.8s

 2 warnings found (use docker --debug to expand):
 - FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 20)
 - FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 58)
```

### 4.2. `./examples/build/Dockerfile` ❌ **FAILED**
- **Purpose:** Example xApp container build and deployment
- **Base image:** `nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubuntu18-c-go:1.9.0` (builder), `ubuntu:18.04` (runtime)
- **Build result:** Failed due to Go module dependency issues
- **Issues found:** 
  - Network connectivity issues with external Go modules
  - Missing dependencies from external Gerrit repositories
  - Go module resolution failures
- **Fixes applied:** 
  - Added `--fix-missing` flag for apt package installation
  - Attempted to use local xapp-frame package instead of external dependencies
  - Modified go.mod to use local package references
- **Status:** Partially fixed but still failing due to complex dependency resolution

**Build Log (Final Attempt):**
```
[+] Building 74.3s (19/25)                                     docker:desktop-linux
 => [internal] load build definition from Dockerfile                           0.0s
 => => transferring dockerfile: 2.90kB                                         0.0s
 => WARN: FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 2  0.0s
 => [internal] load metadata for docker.io/library/ubuntu:18.04                0.0s
 => [internal] load metadata for nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubun  1.2s
 => [internal] load .dockerignore                                              0.0s
 => => transferring context: 55B                                               0.0s
 => [ubuntu-example-xapp  1/13] FROM nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-  0.1s
 => => resolve nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubuntu18-c-go:1.9.0@sh  0.0s
 => [internal] load build context                                              0.1s
 => => transferring context: 12.19kB                                           0.1s
 => CACHED [stage-1 1/7] FROM docker.io/library/ubuntu:18.04@sha256:152dc0424  0.1s
 => => resolve docker.io/library/ubuntu:18.04@sha256:152dc042452c496007f07ca9  0.1s
 => CACHED [ubuntu-example-xapp  2/13] RUN apt update && apt install -y --fix  0.0s
 => CACHED [ubuntu-example-xapp  3/13] RUN wget --content-disposition https:/  0.0s
 => CACHED [ubuntu-example-xapp  4/13] RUN wget --content-disposition https:/  0.0s
 => CACHED [ubuntu-example-xapp  5/13] RUN mkdir -p /go/src/example-xapp       0.0s
 => [ubuntu-example-xapp  6/13] COPY . /go/src/example-xapp                    0.1s
 => [ubuntu-example-xapp  7/13] WORKDIR /go/src/example-xapp                   0.1s
 => [ubuntu-example-xapp  8/13] COPY ../pkg /go/src/gerrit.o-ran-sc.org/r/ric  0.1s
 => [ubuntu-example-xapp  9/13] COPY ../go.mod /go/src/gerrit.o-ran-sc.org/r/  0.1s
 => [ubuntu-example-xapp 10/13] COPY ../go.sum /go/src/gerrit.o-ran-sc.org/r/  0.1s
 => [ubuntu-example-xapp 11/13] RUN sed -i 's|gerrit.o-ran-sc.org/r/ric-plt/x  0.2s
 => [ubuntu-example-xapp 12/13] RUN echo "replace gerrit.o-ran-sc.org/r/ric-p  0.2s
 => ERROR [ubuntu-example-xapp 13/13] RUN go build -a -installsuffix cgo -o   71.9s
------
 > [ubuntu-example-xapp 13/13] RUN go build -a -installsuffix cgo -o example_xapp examples/cmd/example-xapp.go:                                                         
0.222 go: finding github.com/go-openapi/swag v0.22.3
0.222 go: finding github.com/go-logr/logr v1.2.3
0.225 go: finding github.com/mitchellh/mapstructure v1.5.0
0.225 go: finding github.com/prometheus/client_golang v1.15.1
0.230 go: finding github.com/opentracing/opentracing-go v1.2.0
0.232 go: finding github.com/golang/protobuf v1.5.3
0.232 go: finding github.com/oklog/ulid v1.3.1
0.234 go: finding github.com/subosito/gotenv v1.4.2
0.239 go: finding github.com/spf13/jwalterweatherman v1.1.0
2.967 go: finding gerrit.o-ran-sc.org/r/ric-plt/sdlgo.git v0.7.0
3.194 go: finding github.com/stretchr/objx v0.5.0
3.200 go: finding github.com/go-openapi/runtime v0.26.0
3.310 go: finding github.com/go-openapi/errors v0.20.3
3.313 go: finding github.com/spf13/afero v1.9.3
3.348 go: finding github.com/pelletier/go-toml/v2 v2.0.6
3.668 go: finding github.com/spf13/viper v1.15.0
3.837 go: finding github.com/docker/go-units v0.5.0
4.342 go: finding gopkg.in/yaml.v2 v2.4.0
5.340 go: finding gerrit.o-ran-sc.org/r/ric-plt/nodeb-rnib.git/common v1.2.1
5.410 go: finding github.com/mwitkow/go-conntrack v0.0.0-20190716064945-2f068394615f
5.520 go: finding github.com/go-openapi/validate v0.22.1
5.666 go: finding github.com/stretchr/testify v1.6.1
5.669 go: finding github.com/jpillora/backoff v1.0.0
5.756 go: finding github.com/stretchr/testify v1.2.2
6.802 go: finding google.golang.org/api v0.40.0
7.730 go: finding google.golang.org/protobuf v1.26.0
7.748 go: finding google.golang.org/grpc v1.52.0
8.146 go: finding golang.org/x/net v0.7.0
10.74 go: finding golang.org/x/text v0.5.0
10.98 go: finding go.etcd.io/etcd/client/pkg/v3 v3.5.6
11.19 go: finding github.com/go-openapi/loads v0.21.2
11.45 go: finding golang.org/x/xerrors v0.0.0-20220907171357-04be3eba64a2
15.80 go: go.opentelemetry.io/otel@v1.14.0: unrecognized import path "go.opentelemetry.io/otel" (https fetch: Get https://go.opentelemetry.io/otel?go-get=1: dial tcp: lookup go.opentelemetry.io on 192.168.65.7:53: read udp 192.168.65.6:61671->192.168.65.7:53: i/o timeout)                                                                
15.80 go: go.opentelemetry.io/otel/sdk@v1.14.0: unrecognized import path "go.opentelemetry.io/otel/sdk" (https fetch: Get https://go.opentelemetry.io/otel/sdk?go-get=1: dial tcp: lookup go.opentelemetry.io on 192.168.65.7:53: read udp 192.168.65.7:53: read udp 192.168.65.6:61671->192.168.65.7:53: i/o timeout)                                                    
15.82 go: finding github.com/hashicorp/go-cleanhttp v0.5.2
15.82 go: finding github.com/magiconair/properties v1.8.7
16.66 go: finding github.com/hashicorp/serf v0.10.1
17.93 go: finding github.com/beorn7/perks v1.0.1
18.05 go: finding github.com/davecgh/go-spew v1.1.1
18.84 go: finding gopkg.in/ini.v1 v1.67.0
19.07 go: finding golang.org/x/sys v0.5.0
19.24 go: finding gopkg.in/check.v1 v1.0.0-20200227125254-8fa46927fb4f
19.77 go: finding golang.org/x/sys v0.3.0
20.33 go: finding github.com/modern-go/reflect2 v1.0.2
20.43 go: finding github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da
21.40 go: finding gerrit.o-ran-sc.org/r/com/golog.git v0.0.2
21.49 go: finding github.com/mailru/easyjson v0.7.7
21.78 go: finding gerrit.o-ran-sc.org/r/ric-plt/nodeb-rnib.git/reader v1.2.1
22.18 go: finding github.com/pmezard/go-difflib v1.0.0
22.18 go: finding github.com/armon/go-metrics v0.4.0
22.96 go: finding go.uber.org/atomic v1.9.0
23.04 go: finding github.com/cespare/xxhash/v2 v2.1.1
23.05 go: finding github.com/prometheus/common v0.42.0
23.23 go: finding github.com/hashicorp/go-immutable-radix v1.3.1
23.46 go: finding github.com/mattn/go-colorable v0.1.12
24.15 go: finding github.com/googleapis/gax-go/v2 v2.7.0
24.16 go: finding github.com/hashicorp/consul/api v1.18.0
24.48 go: finding github.com/prometheus/procfs v0.9.0
24.49 go: finding github.com/kr/pretty v0.3.1
24.91 go: finding github.com/go-openapi/jsonreference v0.20.0
25.21 go: finding github.com/spf13/pflag v1.0.5
25.25 go: finding github.com/go-openapi/spec v0.20.8
25.32 go: finding gopkg.in/check.v1 v1.0.0-20201130134442-10cb98267c6c
25.36 go: finding go.etcd.io/etcd/api/v3 v3.5.6
25.36 go: finding github.com/stretchr/testify v1.8.1
25.38 go: finding golang.org/x/net v0.4.0
26.12 go: finding golang.org/x/text v0.7.0
26.46 go: finding github.com/hashicorp/golang-lru v0.5.4
26.66 go: finding gopkg.in/check.v1 v0.0.0-20161208181325-20d25e280405
26.68 go: finding github.com/go-openapi/swag v0.21.1
26.77 go: finding github.com/go-logr/stdr v1.2.2
26.80 go: finding github.com/golang/glog v0.0.0-20160126235308-23def4e6c14b
26.85 go: finding golang.org/x/oauth2 v0.0.0-20210218202405-ba52d332ba99
26.96 go: finding gerrit.o-ran-sc.org/r/ric-plt/alarm-go.git/alarm v0.5.14
27.45 go: finding go.uber.org/multierr v1.8.0
27.54 go: finding github.com/pkg/errors v0.9.1
28.01 go: finding github.com/hashicorp/go-rootcerts v1.0.2
28.55 go: finding github.com/google/go-cmp v0.5.5
28.77 go: finding github.com/googleapis/google-cloud-go-testing v0.0.0-20200911160855-bcd43fbb19e8                                                                      
28.89 go: finding cloud.google.com/go/compute v1.12.1
28.94 go: finding golang.org/x/term v0.5.0
29.21 go: finding google.golang.org/genproto v0.0.0-20221227171554-f9683d7f8bef
29.55 go: finding golang.org/x/text v0.9.0
29.57 go: finding github.com/envoyproxy/go-control-plane v0.10.2-0.20220325020618-49ff273808a1                                                                          
30.36 go: finding github.com/hashicorp/go-hclog v1.2.0
30.79 go: finding github.com/go-redis/redis v6.15.9+incompatible
31.63 go: finding golang.org/x/oauth2 v0.0.0-20221014153046-6fdb5e3db783
31.65 go: finding golang.org/x/sys v0.6.0
31.70 go: finding go.opentelemetry.io/otel/trace v1.14.0
32.34 go: finding gerrit.o-ran-sc.org/r/ric-plt/nodeb-rnib.git/entities v1.2.1
32.38 go: finding github.com/golang/protobuf v1.5.2
32.82 go: finding github.com/hashicorp/hcl v1.0.0
32.89 go: finding cloud.google.com/go/firestore v1.9.0
33.34 go: finding golang.org/x/net v0.10.0
33.46 go: finding go.mongodb.org/mongo-driver v1.11.3
33.95 go: finding github.com/go-openapi/strfmt v0.21.7
34.15 go: finding cloud.google.com/go/longrunning v0.3.0
34.70 go: finding github.com/niemeyer/pretty v0.0.0-20200227124842-a10e7caefd8e
35.22 go: finding golang.org/x/crypto v0.0.0-20220525230936-793ad666bf5e
36.17 go: finding github.com/google/uuid v1.3.0
36.89 go: finding golang.org/x/text v0.3.4
37.40 go: finding github.com/go-openapi/jsonpointer v0.19.5
39.31 go: finding go.uber.org/zap v1.21.0
39.44 go: finding k8s.io/utils v0.0.0-20230505201702-9f6742963106
39.59 go: finding github.com/stretchr/testify v1.7.5
40.03 go: finding go.etcd.io/etcd/client/v3 v3.5.6
40.08 go: finding github.com/census-instrumentation/opencensus-proto v0.2.1
41.18 go: finding github.com/kr/text v0.2.0
42.14 go: finding github.com/googleapis/enterprise-certificate-proxy v0.2.1
42.28 go: finding github.com/pkg/sftp v1.13.1
42.63 go: finding cloud.google.com/go/compute/metadata v0.2.3
42.74 go: finding google.golang.org/appengine v1.6.7
43.56 go: finding golang.org/x/sync v0.1.0
44.10 go: finding cloud.google.com/go/compute v1.14.0
44.38 go: finding github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd
44.92 go: finding github.com/stretchr/testify v1.3.0
44.95 go: finding github.com/cncf/xds/go v0.0.0-20211011173535-cb28da3451f1
46.35 go: finding github.com/coreos/go-systemd/v22 v22.3.2
47.01 go: finding cloud.google.com/go v0.105.0
48.27 go: finding github.com/envoyproxy/protoc-gen-validate v0.1.0
48.81 go: finding gopkg.in/yaml.v3 v3.0.1
49.64 go: finding github.com/asaskevich/govalidator v0.0.0-20230301143203-a9d515a09cc2                                                                                  
49.87 go: finding github.com/mattn/go-isatty v0.0.14
51.86 go: finding github.com/go-openapi/analysis v0.21.2
52.49 go: finding golang.org/x/oauth2 v0.5.0
52.53 go: finding github.com/sagikazarmark/crypt v0.9.0
52.61 go: finding github.com/go-openapi/strfmt v0.21.1
53.59 go: finding github.com/go-openapi/errors v0.19.9
54.05 go: finding github.com/spf13/cast v1.5.0
54.40 go: finding cloud.google.com/go/storage v1.14.0
54.66 go: finding github.com/prometheus/common v0.43.0
55.10 go: finding github.com/stretchr/testify v1.7.0
55.48 go: finding github.com/prometheus/client_model v0.3.0
56.10 go: finding github.com/go-openapi/loads v0.21.1
56.61 go: finding github.com/cncf/udpa/go v0.0.0-20210930031921-04548b0d99d4
56.71 go: finding golang.org/x/tools v0.0.0-20190614205625-5aca471b1d59
57.59 go: finding github.com/stretchr/objx v0.1.0
57.72 go: finding github.com/fatih/color v1.13.0
57.87 go: finding github.com/go-openapi/spec v0.20.4
58.31 go: finding github.com/mitchellh/go-homedir v1.1.0
58.37 go: finding github.com/gorilla/mux v1.8.0
58.98 go: finding github.com/stretchr/testify v1.8.2
59.22 go: finding github.com/jessevdk/go-flags v1.5.0
60.63 go: finding github.com/stretchr/testify v1.8.0
60.63 go: finding github.com/google/go-cmp v0.5.9
60.64 go: finding gopkg.in/yaml.v3 v3.0.0-20200313102051-9f266ea9e77c
60.66 go: finding github.com/stretchr/testify v1.7.0
60.80 go: finding cloud.google.com/go/compute/metadata v0.2.1
60.88 go: finding github.com/matttproud/golang_protobuf_extensions v1.0.4
62.38 go: finding google.golang.org/protobuf v1.28.1
62.48 go: finding go.etcd.io/etcd/client/v2 v2.305.6
62.53 go: finding github.com/go-openapi/spec v0.20.9
62.65 go: finding github.com/prometheus/client_model v0.4.0
63.15 go: finding github.com/davecgh/go-spew v1.1.0
63.21 go: finding github.com/go-openapi/analysis v0.21.4
63.74 go: finding github.com/golang/protobuf v1.5.0
63.83 go: finding github.com/coreos/go-semver v0.3.0
64.04 go: finding github.com/josharian/intern v1.0.0
64.43 go: finding golang.org/x/crypto v0.0.0-20211108221036-ceb1ce70b4fa
64.47 go: finding github.com/gogo/protobuf v1.3.2
64.49 go: finding google.golang.org/genproto v0.0.0-20221118155620-16455021b5e6
64.51 go: finding github.com/cespare/xxhash/v2 v2.2.0
64.88 go: finding github.com/json-iterator/go v1.1.12
65.27 go: finding google.golang.org/protobuf v1.30.0
65.76 go: finding golang.org/x/sys v0.8.0
66.56 go: finding go.opencensus.io v0.24.0
71.79 go: error loading module requirements
------
```