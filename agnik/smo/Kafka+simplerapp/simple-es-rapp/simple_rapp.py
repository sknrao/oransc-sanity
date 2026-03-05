"""
Simple Energy Saving rApp — Data + Decision + Action
=====================================================
Data:    Read PM data from Kafka topic (message bus)
Decision: Simple threshold (if PRB usage < 20% → power off cell)
Action:   PATCH NRCellDU administrativeState via SDNR RESTCONF (O1)

Runs inside k8s where Kafka DNS resolves.
"""

import json
import time
import os
import logging

# ─── CONFIG (from env vars or defaults) ───────────────
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "onap-strimzi-kafka-bootstrap.onap:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "unauthenticated.SEC_3GPP_PERFORMANCEASSURANCE_OUTPUT")
KAFKA_GROUP = os.getenv("KAFKA_GROUP", "simple-es-rapp-group")
KAFKA_USER = os.getenv("KAFKA_USER", "strimzi-kafka-admin")
KAFKA_PASS = os.getenv("KAFKA_PASS", "G7ITDUBrDBRlZmSKtEMYt9sY2k1ZfBn2")

SDNR_URL = os.getenv("SDNR_URL", "http://sdnc.onap:8282")
SDNR_USER = os.getenv("SDNR_USER", "admin")
SDNR_PASS = os.getenv("SDNR_PASS", "Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U")

NODE = os.getenv("NODE", "SOMETHING")
ME = os.getenv("ME", "ManagedElement-002")
GNB = os.getenv("GNB", "GNBDUFunction-001")

PRB_THRESHOLD = float(os.getenv("PRB_THRESHOLD", "20.0"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("simple-rapp")

# ─── DATA: Kafka Consumer ─────────────────────────────

def create_kafka_consumer():
    from confluent_kafka import Consumer
    conf = {
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': KAFKA_GROUP,
        'auto.offset.reset': 'latest',
        'security.protocol': 'SASL_PLAINTEXT',
        'sasl.mechanism': 'SCRAM-SHA-512',
        'sasl.username': KAFKA_USER,
        'sasl.password': KAFKA_PASS,
    }
    consumer = Consumer(conf)
    consumer.subscribe([KAFKA_TOPIC])
    log.info(f"Kafka consumer created, topic: {KAFKA_TOPIC}")
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
                cell = meas_val.get("measObjInstId", "unknown")
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
    import requests
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
    import requests
    try:
        r = requests.get(cell_url(cell_id), auth=(SDNR_USER, SDNR_PASS),
                        headers={"Accept": "application/json"}, timeout=10)
        if r.status_code == 200:
            return r.json().get("_3gpp-nr-nrm-nrcelldu:attributes", {}).get("administrativeState", "?")
    except:
        pass
    return "?"


# ─── MAIN ─────────────────────────────────────────────

def main():
    log.info("=" * 50)
    log.info("  Simple Energy Saving rApp")
    log.info("  Kafka -> Threshold -> SDNR RESTCONF")
    log.info("=" * 50)

    # DATA
    log.info("\n--- PHASE 1: DATA (Kafka) ---")
    consumer = create_kafka_consumer()
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

    log.info("\n" + "=" * 50)
    log.info("  Done! Data -> Decision -> Action complete")
    log.info("=" * 50)
    try:
        consumer.close()
    except:
        pass


if __name__ == "__main__":
    main()
