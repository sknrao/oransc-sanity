# ric-app-kpimon-go CVE Fixes

## Fixed CVEs

- **CVE-2024-34043**
  - **File:** wrapper.c
  - **Fix Applied:** Added NULL pointer checks for choice union members: initiatingMessage, successfulOutcome, unsuccessfulOutcome
  - **Explanation:** Prevents segmentation faults when processing malformed or partially decoded E2AP-PDU messages.
