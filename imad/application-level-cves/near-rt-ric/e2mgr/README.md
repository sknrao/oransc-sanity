# e2mgr CVE Fixes

## Fixed CVEs

- **CVE-2024-34048**
  - **File:** e2_node_config_update_notification_handler.go
  - **Fix Applied:** Replaced incorrect array indexing [i] with [j] in inner loops for both GNB and ENB
  - **Explanation:** Prevents out-of-bounds access when updating NodeConfigs, avoiding runtime panics.

- **CVE-2024-34047**
  - **File:** ric_service_update_handler.go
  - **Fix Applied:** Added array bounds and maximum size checks in RicServiceUpdateHandler
  - **Explanation:** Ensures safe indexing of RAN function lists and prevents resource exhaustion.
