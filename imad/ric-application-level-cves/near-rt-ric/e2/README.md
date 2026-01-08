# e2 CVE Fixes

## Fixed CVEs

- **CVE-2024-34046**
  - **File:** sctpThread.cpp
  - **Fix Applied:** Added NULL pointer checks before e2tCounters increments
  - **Explanation:** Prevents crashes due to dereferencing NULL peerInfo pointers during Prometheus metric updates.

- **CVE-2024-34045**
  - **File:** sctpThread.cpp
  - **Fix Applied:** Added NULL pointer checks before Prometheus counter increments in E2setup handlers
  - **Explanation:** Prevents segmentation faults when E2setup counters are uninitialized.

- **CVE-2024-34044**
  - **File:** sctpThread.cpp
  - **Fix Applied:** Added NULL pointer checks in buildPrometheusList and guarded Prometheus initialization calls
  - **Explanation:** Prevents segmentation faults when peerInfo or prometheusFamily is NULL, ensuring stability.
