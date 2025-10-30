# e2mgr CVE Fixes

## Fixed CVEs

* **CVE-2024-34048**

  * **File:** `e2_node_config_update_notification_handler.go`
  * **Fix Applied:** Replaced incorrect array indexing `[i]` with `[j]` in inner loops for both GNB and ENB
  * **Explanation:** Prevents out-of-bounds access when updating NodeConfigs, avoiding runtime panics.

* **CVE-2024-34047**

  * **File:** `ric_service_update_handler.go`
  * **Fix Applied:** Added array bounds and maximum size checks in `RicServiceUpdateHandler`
  * **Explanation:** Ensures safe indexing of RAN function lists and prevents resource exhaustion.

* **CVE-2024-34035**

  * **File:** `services/rmr_message_throttler.go`
  * **Fix Applied:** Added RMR message throttling mechanism with per-RAN rate limits
  * **Explanation:** Prevents denial of service through RMR message flooding by limiting message processing rate and dropping excess messages safely.

* **CVE-2023-42358**

  * **Files:** `middleware/rate_limiter.go`, `middleware/timeout.go`, `httpserver/http_server.go`
  * **Fix Applied:** Implemented HTTP rate limiting and request timeout middleware
  * **Explanation:** Blocks crafted or excessive API requests by enforcing per-IP rate limits and timeouts, preventing denial-of-service attacks through the Subscription Manager API.