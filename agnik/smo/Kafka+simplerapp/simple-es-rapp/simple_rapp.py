"""
Simple Energy Saving rApp — Data + Decision + Action
=====================================================
Data:    Read PM data from Kafka topic (message bus)
Decision: Simple threshold (if PRB usage < 20% → power off cell)
Action:   PATCH NRCellDU administrativeState via SDNR RESTCONF (O1)

Kafka authentication:
  - Uses OAuth2 / OAUTHBEARER via Keycloak (dynamic token fetch)
  - No hardcoded passwords
  - Token is fetched from AUTH_SERVICE_URL using CLIENT_ID + CLIENT_SECRET

Runs inside k8s where Kafka DNS resolves.
"""

import json
import time
import os
import logging
import requests

# ─── CONFIG (from env vars or defaults) ───────────────
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "onap-strimzi-kafka-bootstrap.onap:9095")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "pmreports")
KAFKA_GROUP = os.getenv("KAFKA_GROUP", "simple-es-rapp-group")

# OAuth2 credentials for Kafka (fetched dynamically from Keycloak)
AUTH_SERVICE_URL = os.getenv(
    "AUTH_SERVICE_URL",
    "http://keycloak.smo:8080/realms/nonrtric-realm/protocol/openid-connect/token"
)
CREDS_CLIENT_ID = os.getenv("CREDS_CLIENT_ID", "simple-es-rapp")
CREDS_CLIENT_SECRET = os.getenv("CREDS_CLIENT_SECRET", "")
CREDS_GRANT_TYPE = os.getenv("CREDS_GRANT_TYPE", "client_credentials")

# SDNR config
SDNR_URL = os.getenv("SDNR_URL", "http://sdnc.onap:8282")
SDNR_USER = os.getenv("SDNR_USER", "admin")
SDNR_PASS = os.getenv("SDNR_PASS", "Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U")

NODE = os.getenv("NODE", "SOMETHING")
ME = os.getenv("ME", "ManagedElement-002")
GNB = os.getenv("GNB", "GNBDUFunction-001")

PRB_THRESHOLD = float(os.getenv("PRB_THRESHOLD", "20.0"))
POLL_INTERVAL_SEC = int(os.getenv("POLL_INTERVAL_SEC", "60"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("simple-rapp")


# ─── OAUTH: Dynamic Token Fetch ──────────────────────

def fetch_oauth_token():
    """
    Fetch an OAuth2 access token from Keycloak using client_credentials grant.
    This is the same approach used by the official O-RAN pm-rapp (main.go).
    """
    if not AUTH_SERVICE_URL:
        log.warning("AUTH_SERVICE_URL not set — skipping OAuth, using SASL_PLAINTEXT")
        return None

    payload = {
        "grant_type": CREDS_GRANT_TYPE,
        "client_id": CREDS_CLIENT_ID,
    }
    if CREDS_CLIENT_SECRET:
        payload["client_secret"] = CREDS_CLIENT_SECRET

    try:
        resp = requests.post(AUTH_SERVICE_URL, data=payload, timeout=10)
        if resp.status_code == 200:
            token = resp.json().get("access_token", "")
            log.info("[AUTH] OAuth token fetched successfully from Keycloak")
            return token
        else:
            log.error(f"[AUTH] Token fetch failed: HTTP {resp.status_code} — {resp.text[:200]}")
            return None
    except Exception as e:
        log.error(f"[AUTH] Cannot reach Keycloak: {e}")
        return None


def _oauth_token_cb(config_str):
    """
    Callback for confluent_kafka OAUTHBEARER token refresh.
    Called automatically by the Kafka client when the token needs refreshing.
    """
    token = fetch_oauth_token()
    if token:
        return token, time.time() + 300  # token valid for 5 min
    raise Exception("Failed to fetch OAuth token")


# ─── DATA: Kafka Consumer ─────────────────────────────

def _oauth_cb(config_str):
    """
    Callback invoked by confluent-kafka when it needs an OAUTHBEARER token.
    Fetches a fresh JWT from Keycloak each time.
    """
    token = fetch_oauth_token()
    if token:
        return token, time.time() + 300  # token, expiry epoch
    raise Exception("Failed to fetch OAuth token from Keycloak")


def create_kafka_consumer():
    from confluent_kafka import Consumer

    # First, try to fetch a token to decide auth method
    token = fetch_oauth_token()

    if token:
        # Use OAUTHBEARER with SASL_PLAINTEXT (port 9095)
        log.info("[KAFKA] Using OAUTHBEARER authentication (dynamic token)")
        conf = {
            'bootstrap.servers': KAFKA_BOOTSTRAP,
            'group.id': f"{KAFKA_GROUP}-{int(time.time())}",
            'auto.offset.reset': 'earliest',
            'security.protocol': 'SASL_PLAINTEXT',
            'sasl.mechanism': 'OAUTHBEARER',
            'oauth_cb': _oauth_cb,
        }
        consumer = Consumer(conf)
    else:
        # Fallback: try SASL_PLAINTEXT with SCRAM-SHA-512 using admin creds
        log.warning("[KAFKA] OAuth failed — falling back to SCRAM-SHA-512")
        kafka_user = os.getenv("KAFKA_USER", "strimzi-kafka-admin")
        kafka_pass = os.getenv("KAFKA_PASS", "")
        if not kafka_pass:
            log.error("[KAFKA] No KAFKA_PASS set and OAuth failed. Cannot connect.")
            return None
        conf = {
            'bootstrap.servers': KAFKA_BOOTSTRAP,
            'group.id': f"{KAFKA_GROUP}-{int(time.time())}",
            'auto.offset.reset': 'earliest',
            'security.protocol': 'SASL_PLAINTEXT',
            'sasl.mechanism': 'SCRAM-SHA-512',
            'sasl.username': kafka_user,
            'sasl.password': kafka_pass,
        }
        consumer = Consumer(conf)

    consumer.subscribe([KAFKA_TOPIC])
    log.info(f"[KAFKA] Consumer created, topic: {KAFKA_TOPIC}, group: {conf['group.id']}")
    return consumer


def read_kafka_messages(consumer, max_messages=5, timeout_sec=30):
    messages = []
    start = time.time()
    while len(messages) < max_messages and (time.time() - start) < timeout_sec:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            log.warning(f"Kafka error: {msg.error()}")
            continue
        try:
            value = json.loads(msg.value().decode('utf-8'))
            messages.append(value)
            log.info(f"[DATA] Message #{len(messages)} | partition={msg.partition()} offset={msg.offset()}")
            log.info(f"[DATA]   keys: {list(value.get('event',value).keys())}")
        except Exception as e:
            log.warning(f"Cannot parse: {e}")
    log.info(f"[DATA] Total: {len(messages)} messages in {time.time()-start:.1f}s")
    return messages


# ─── DECISION: Threshold ──────────────────────────────

def make_decision(pm_data):
    decisions = []
    for msg in pm_data:
        event = msg.get("event", msg)
        perf_data = event.get("perf3gppFields", event.get("measurementFields", {}))
        meas_collection = perf_data.get("measDataCollection", {})
        for meas_info in meas_collection.get("measInfoList", []):
            meas_types = meas_info.get("measTypes", {}).get("sMeasTypesList", [])
            for meas_val in meas_info.get("measValuesList", []):
                raw_cell = meas_val.get("measObjInstId", "unknown")
                cell = raw_cell
                if "NRCellDU=" in raw_cell:
                    cell = raw_cell.split("NRCellDU=")[-1].split(",")[0]
                for result in meas_val.get("measResults", []):
                    p = result.get("p", 0)
                    s_value = result.get("sValue", "0")
                    if p > 0 and p <= len(meas_types):
                        field = meas_types[p - 1]
                    else:
                        field = f"field_{p}"
                    if "PrbUsedUl" in field:
                        try:
                            prb = float(s_value)
                            action = "LOCKED" if prb < PRB_THRESHOLD else "UNLOCKED"
                            decisions.append({"cell": cell, "prb": prb, "action": action})
                            log.info(f"[DECISION] {cell}: PRB={prb:.1f}% -> {action}")
                        except ValueError:
                            pass

    if not decisions:
        log.info("[DECISION] No PRB data in messages — using demo decision")
        decisions.append({"cell": "S1-B12-C1", "prb": 10.0, "action": "LOCKED"})
    return decisions


# ─── ACTION: SDNR RESTCONF ────────────────────────────

def cell_url(cell_id):
    return (
        f"{SDNR_URL}/rests/data/network-topology:network-topology"
        f"/topology=topology-netconf/node={NODE}/yang-ext:mount"
        f"/_3gpp-common-managed-element:ManagedElement={ME}"
        f"/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction={GNB}"
        f"/_3gpp-nr-nrm-nrcelldu:NRCellDU={cell_id}/attributes"
    )


def set_admin_state(cell_id, state):
    body = {"_3gpp-nr-nrm-nrcelldu:attributes": {"administrativeState": state}}
    try:
        r = requests.patch(cell_url(cell_id), json=body,
                          auth=(SDNR_USER, SDNR_PASS),
                          headers={"Content-Type": "application/json"}, timeout=10)
        log.info(f"[ACTION] Cell {cell_id} -> {state}: HTTP {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        log.error(f"[ACTION] Error: {e}")
        return False


def get_admin_state(cell_id):
    try:
        r = requests.get(cell_url(cell_id), auth=(SDNR_USER, SDNR_PASS),
                        headers={"Accept": "application/json"}, timeout=10)
        if r.status_code == 200:
            return r.json().get("_3gpp-nr-nrm-nrcelldu:attributes", {}).get("administrativeState", "?")
    except:
        pass
    return "?"


# ─── RUN ONE CYCLE ────────────────────────────────────

def run_cycle(consumer):
    """Execute one Data -> Decision -> Action cycle."""
    # DATA
    log.info("\n--- PHASE 1: DATA (Kafka) ---")
    messages = read_kafka_messages(consumer, max_messages=3, timeout_sec=20)

    # DECISION
    log.info("\n--- PHASE 2: DECISION (Threshold) ---")
    decisions = make_decision(messages)

    # ACTION
    log.info("\n--- PHASE 3: ACTION (SDNR) ---")
    for d in decisions:
        cell, action = d["cell"], d["action"]
        current = get_admin_state(cell)
        log.info(f"  {cell}: current={current}, target={action}")
        if current != action:
            set_admin_state(cell, action)
            time.sleep(1)
            log.info(f"  Verified: {cell} = {get_admin_state(cell)}")
        else:
            log.info(f"  Already {action}, skip")

    # Restore
    log.info("\n--- Restore to UNLOCKED ---")
    set_admin_state("S1-B12-C1", "UNLOCKED")

    log.info(f"\n--- Cycle complete. Sleeping {POLL_INTERVAL_SEC}s ---")


# ─── MAIN (CONTINUOUS LOOP) ──────────────────────────

def main():
    log.info("=" * 50)
    log.info("  Simple Energy Saving rApp (Continuous)")
    log.info("  Kafka -> Threshold -> SDNR RESTCONF")
    log.info("  Auth: OAuth2 via Keycloak (dynamic token)")
    log.info("=" * 50)

    consumer = create_kafka_consumer()
    if consumer is None:
        log.error("Cannot create Kafka consumer. Exiting.")
        return

    cycle = 0
    try:
        while True:
            cycle += 1
            log.info(f"\n{'='*50}")
            log.info(f"  Cycle #{cycle}")
            log.info(f"{'='*50}")
            run_cycle(consumer)
            time.sleep(POLL_INTERVAL_SEC)
    except KeyboardInterrupt:
        log.info("Shutting down...")
    finally:
        try:
            consumer.close()
        except:
            pass

    log.info("Done.")


if __name__ == "__main__":
    main()
