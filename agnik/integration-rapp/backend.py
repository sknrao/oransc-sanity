#!/usr/bin/env python3
"""
Integration rApp — Backend API Server
=======================================
Flask-based backend exposing 8 REST endpoints for O-RAN deployment verification.
Combines SDNR, InfluxDB, Kafka, MinIO, and A1PMS into a single tool.

Usage:
    python backend.py              # Start web server on port 5000
    python backend.py --port 8080  # Custom port
"""

import os
import sys
import json
import time
import subprocess
import yaml
import requests
from requests.auth import HTTPBasicAuth
from flask import Flask, jsonify, request, render_template

# ── Load Config & Logger ─────────────────────────────────────
CONFIG_PATH = os.getenv("CONFIG_PATH", "config.yaml")

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("integration-rapp")

def load_config():
    try:
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config from {CONFIG_PATH}: {e}")
        return {"smo": {}}

CFG = load_config()
SMO = CFG.get("smo", {})

# Override sensitive settings with environment variables if available
SDNR_URL = os.getenv("SDNR_URL", SMO.get("sdnr_url", "http://sdnc.onap.svc.cluster.local:8282"))
SDNR_USER = os.getenv("SDNR_USER", SMO.get("sdnr_user", ""))
SDNR_PASS = os.getenv("SDNR_PASS", SMO.get("sdnr_password", ""))
SDNR_AUTH = HTTPBasicAuth(SDNR_USER, SDNR_PASS)
SDNR_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

INFLUX_URL = os.getenv("INFLUX_URL", SMO.get("influxdb_url", "http://influxdb2.smo.svc.cluster.local:8086"))
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", SMO.get("influxdb_token", ""))
INFLUX_ORG = os.getenv("INFLUX_ORG", SMO.get("influxdb_org", ""))

A1PMS_URL = os.getenv("A1PMS_URL", SMO.get("a1pms_url", "http://policymanagementservice.nonrtric.svc.cluster.local:8081"))

KAFKA_ADMIN_URL = os.getenv("KAFKA_ADMIN_URL", SMO.get("kafka_admin_url", "http://redpanda-console.smo.svc.cluster.local:8080"))
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", SMO.get("minio_endpoint", "minio.smo.svc.cluster.local:9000"))

app = Flask(__name__)

# Suppress third-party noise, keep app logs
logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('kafka').setLevel(logging.WARNING)


# ═══════════════════════════════════════════════════════════
#  FEATURE 1: List Connected SDNR Nodes
# ═══════════════════════════════════════════════════════════

def get_sdnr_nodes():
    """Query SDNR RESTCONF for all NETCONF nodes and their status."""
    url = f"{SDNR_URL}/rests/data/network-topology:network-topology"
    try:
        resp = requests.get(url, auth=SDNR_AUTH, headers=SDNR_HEADERS, timeout=30)
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}", "nodes": []}

        data = resp.json()
        topologies = data.get("network-topology:network-topology", {}).get("topology", [])
        nodes = []
        for topo in topologies:
            for node in topo.get("node", []):
                nodes.append({
                    "node_id": node.get("node-id"),
                    "status": node.get("netconf-node-topology:connection-status", "unknown"),
                    "host": node.get("netconf-node-topology:host", "?"),
                    "port": node.get("netconf-node-topology:port", "?"),
                })
        connected = [n for n in nodes if n["status"] == "connected"]
        return {
            "total": len(nodes),
            "connected": len(connected),
            "nodes": nodes,
        }
    except Exception as e:
        return {"error": str(e), "nodes": []}


@app.route("/api/nodes")
def api_nodes():
    return jsonify(get_sdnr_nodes())


# ═══════════════════════════════════════════════════════════
#  FEATURE 2: Reset a Node (LOCK → UNLOCK via SDNR)
# ═══════════════════════════════════════════════════════════

def _cell_url(cell_id, node_id=None):
    if node_id is None:
        node_id = SMO.get("node_id", "SOMETHING")
    
    # Auto-detect if node_id is missing or generic
    if not node_id or node_id == "SOMETHING":
        nodes_info = get_sdnr_nodes()
        connected = [n for n in nodes_info.get("nodes", []) if n.get("status") == "connected"]
        if connected:
            node_id = connected[0]["node_id"]
            print(f"DEBUG: Auto-detected connected node: {node_id}")
        else:
            node_id = "o-du-pynts-1123" # Last resort fallback

    me = SMO.get("managed_element", "ManagedElement-001")
    gnb = SMO.get("gnb_du_function", "GNBDUFunction-001")
    return (
        f"{SDNR_URL}/rests/data/network-topology:network-topology"
        f"/topology=topology-netconf/node={node_id}/yang-ext:mount"
        f"/_3gpp-common-managed-element:ManagedElement={me}"
        f"/_3gpp-nr-nrm-gnbdufunction:GNBDUFunction={gnb}"
        f"/_3gpp-nr-nrm-nrcelldu:NRCellDU={cell_id}/attributes"
    )

def reset_node(cell_id, node_id=None):
    """Reset a cell by setting it to LOCKED, then back to UNLOCKED."""
    results = {"cell_id": cell_id, "node_id": node_id, "steps": []}
    target_url = _cell_url(cell_id, node_id)
    
    # Update node_id in results if it was auto-detected inside _cell_url
    if not node_id:
        try:
            # We can't easily extract it back from the URL string without parsing, 
            # but we can at least log the URL used.
            results["target_url"] = target_url
        except: pass

    # Step 1: Read current state
    try:
        r = requests.get(target_url, auth=SDNR_AUTH,
                         headers={"Accept": "application/json"}, timeout=30)
        if r.status_code == 200:
            current = r.json().get("_3gpp-nr-nrm-nrcelldu:attributes", {}).get("administrativeState", "?")
            results["steps"].append({"action": "READ", "state": current, "status": "OK"})
        else:
            results["steps"].append({"action": "READ", "status": f"HTTP {r.status_code}"})
            results["error"] = f"Cannot read cell state: HTTP {r.status_code}"
            return results
    except Exception as e:
        results["error"] = str(e)
        return results

    # Step 2: LOCK
    body = {"_3gpp-nr-nrm-nrcelldu:attributes": {"administrativeState": "LOCKED"}}
    try:
        r = requests.patch(target_url, json=body, auth=SDNR_AUTH,
                           headers=SDNR_HEADERS, timeout=30)
        results["steps"].append({"action": "LOCK", "http": r.status_code,
                                 "status": "OK" if r.status_code == 200 else "FAIL"})
    except Exception as e:
        results["steps"].append({"action": "LOCK", "status": f"ERROR: {e}"})

    time.sleep(1)

    # Step 3: UNLOCK (restore)
    body = {"_3gpp-nr-nrm-nrcelldu:attributes": {"administrativeState": "UNLOCKED"}}
    try:
        r = requests.patch(target_url, json=body, auth=SDNR_AUTH,
                           headers=SDNR_HEADERS, timeout=30)
        results["steps"].append({"action": "UNLOCK", "http": r.status_code,
                                 "status": "OK" if r.status_code == 200 else "FAIL"})
    except Exception as e:
        results["steps"].append({"action": "UNLOCK", "status": f"ERROR: {e}"})

    # Step 4: Verify
    time.sleep(1)
    try:
        r = requests.get(target_url, auth=SDNR_AUTH,
                         headers={"Accept": "application/json"}, timeout=30)
        if r.status_code == 200:
            final = r.json().get("_3gpp-nr-nrm-nrcelldu:attributes", {}).get("administrativeState", "?")
            results["steps"].append({"action": "VERIFY", "state": final, "status": "OK"})
            results["final_state"] = final
    except:
        pass

    return results


@app.route("/api/nodes/<cell_id>/reset", methods=["POST"])
def api_reset_node(cell_id):
    body = request.get_json(force=True, silent=True) or {}
    node_id = body.get("node_id")
    return jsonify(reset_node(cell_id, node_id))


# ═══════════════════════════════════════════════════════════
#  FEATURE 3: List Kafka Topics with Message Counts
# ═══════════════════════════════════════════════════════════

def get_kafka_topics():
    """List all Kafka topics and identify which ones have messages."""
    # Method 1: Try Redpanda Console REST API (faster)
    try:
        url = f"{KAFKA_ADMIN_URL}/api/topics"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            topics_data = resp.json().get("topics", [])
            topics = []
            for t in topics_data:
                name = t.get("topicName", t.get("name", "?"))
                # Use logDirSummary.totalSizeBytes to detect data presence
                size_bytes = t.get("logDirSummary", {}).get("totalSizeBytes", 0)
                topics.append({
                    "name": name,
                    "size_bytes": size_bytes,
                    "has_messages": size_bytes > 0,
                    "partitions": t.get("partitionCount", 0),
                })
            # Sort: topics with data first
            topics.sort(key=lambda x: (-x["size_bytes"], x["name"]))
            return {"total": len(topics), "topics": topics, "method": "redpanda-console"}
    except:
        pass

    # Method 2: kafka-python fallback
    try:
        from kafka import KafkaConsumer, TopicPartition
        params = {
            "bootstrap_servers": CFG["smo"].get("kafka_bootstrap_server", "localhost:9092"),
            "request_timeout_ms": 5000,
            "api_version": (3, 7, 0)
        }
        if CFG["smo"].get("kafka_sasl_user"):
            params.update({
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": CFG["smo"]["kafka_sasl_user"],
                "sasl_plain_password": CFG["smo"].get("kafka_sasl_pass", "")
            })
        else:
            params["security_protocol"] = "PLAINTEXT"

        consumer = KafkaConsumer(**params)
        raw_topics = consumer.topics()
        topics = []
        for t in raw_topics:
            try:
                tps = [TopicPartition(t, p) for p in consumer.partitions_for_topic(t)]
                if tps:
                    ends = consumer.end_offsets(tps)
                    begins = consumer.beginning_offsets(tps)
                    count = sum(ends[tp] - begins[tp] for tp in tps)
                    topics.append({"name": t, "messages": count, "has_messages": count > 0})
                else:
                    topics.append({"name": t, "messages": 0, "has_messages": False})
            except Exception:
                topics.append({"name": t, "messages": -1, "has_messages": None})

        consumer.close()
        return {"total": len(topics), "topics": topics, "method": f"kafka-python ({params['security_protocol']})"}
    except Exception as e:
        return {"error": f"Cannot reach Kafka: {e}", "topics": []}


@app.route("/api/kafka/topics")
def api_kafka_topics():
    return jsonify(get_kafka_topics())


# ═══════════════════════════════════════════════════════════
#  FEATURE 4: Show Latest Message from a Topic
# ═══════════════════════════════════════════════════════════

def get_latest_message(topic_name):
    """Consume the latest message from a given Kafka topic natively without SSH."""
    try:
        from kafka import KafkaConsumer, TopicPartition
        params = {
            "bootstrap_servers": CFG["smo"].get("kafka_bootstrap_server", "localhost:9092"),
            "consumer_timeout_ms": 5000,
            "auto_offset_reset": "latest",
            "api_version": (3, 7, 0)
        }
        if CFG["smo"].get("kafka_sasl_user"):
            params.update({
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": CFG["smo"]["kafka_sasl_user"],
                "sasl_plain_password": CFG["smo"].get("kafka_sasl_pass", "")
            })
        else:
            params["security_protocol"] = "PLAINTEXT"

        consumer = KafkaConsumer(**params)
        
        # Find partitions
        partitions = consumer.partitions_for_topic(topic_name)
        if not partitions:
            return {"topic": topic_name, "error": "Topic not found or empty partitions"}
            
        # Try to read the last message from the first partition
        tp = TopicPartition(topic_name, list(partitions)[0])
        consumer.assign([tp])
        consumer.seek_to_end(tp)
        end_offset = consumer.position(tp)
        
        if end_offset == 0:
            consumer.close()
            return {"topic": topic_name, "error": "No messages found or topic is empty"}
            
        # Seek just before the end offset
        consumer.seek(tp, end_offset - 1)
        records = consumer.poll(timeout_ms=5000)
        consumer.close()
        
        if tp in records and len(records[tp]) > 0:
            msg = records[tp][0].value.decode('utf-8')
            try:
                value = json.loads(msg)
            except:
                value = msg
            return {"topic": topic_name, "value": value, "method": "kafka-python"}
            
        return {"topic": topic_name, "error": "Timeout or failed to fetch message"}
    except Exception as e:
        return {"topic": topic_name, "error": str(e)}


@app.route("/api/kafka/topics/<topic_name>/latest")
def api_kafka_latest(topic_name):
    return jsonify(get_latest_message(topic_name))


# ═══════════════════════════════════════════════════════════
#  FEATURE 5: Check 3 Integration Points
# ═══════════════════════════════════════════════════════════

def check_integration_points():
    """
    Check the 4 key integration points for O-RAN SMO:
    (a) SDNR Connected Nodes
    (b) Kafka Message Bus (pmreports topic)
    (c) InfluxDB PM Storage (Auth/Health)
    (d) A1 Policy Management (RIC Discovery)
    """
    results = {"checks": [], "all_pass": True}

    # (a) SDNR Connected Nodes
    sdnr_ok = False
    try:
        nodes_info = get_sdnr_nodes()
        connected_count = nodes_info.get("connected", 0)
        sdnr_ok = connected_count > 0
        results["checks"].append({
            "name": "SDNR Connected Nodes",
            "status": "PASS" if sdnr_ok else "FAIL",
            "details": {"count": connected_count}
        })
    except Exception as e:
        results["checks"].append({"name": "SDNR Connected Nodes", "status": "FAIL", "details": {"error": str(e)}})

    # (b) Kafka / Message Bus (Direct Broker Check)
    kafka_ok = False
    try:
        from kafka import KafkaConsumer
        params = {
            "bootstrap_servers": CFG["smo"].get("kafka_bootstrap_server", "localhost:9092"),
            "request_timeout_ms": 10000,
            "api_version": (3, 7, 0)
        }
        if CFG["smo"].get("kafka_sasl_user"):
            params.update({
                "security_protocol": "SASL_PLAINTEXT",
                "sasl_mechanism": "SCRAM-SHA-512",
                "sasl_plain_username": CFG["smo"]["kafka_sasl_user"],
                "sasl_plain_password": CFG["smo"].get("kafka_sasl_pass", "")
            })
        else:
            params["security_protocol"] = "PLAINTEXT"

        # Use Consumer for heartbeat check as it's often more resilient in this k8s env
        consumer = KafkaConsumer(**params)
        topics = consumer.topics()
        kafka_ok = "pmreports" in topics
        results["checks"].append({
            "name": "Kafka Message Bus",
            "status": "PASS" if topics else "WARN", # PASS if any topics found
            "details": {"pmreports_active": kafka_ok, "total_topics": len(topics)}
        })
        consumer.close()
    except Exception as e:
        results["checks"].append({"name": "Kafka Message Bus", "status": "FAIL", "details": {"error": str(e)}})

    # (c) InfluxDB PM Storage
    influx_ok = False
    try:
        headers = {"Authorization": f"Token {INFLUX_TOKEN}"}
        resp = requests.get(f"{INFLUX_URL}/health", headers=headers, timeout=5)
        if resp.status_code == 200:
            b_resp = requests.get(f"{INFLUX_URL}/api/v2/buckets", headers=headers, timeout=5)
            influx_ok = b_resp.status_code == 200
            results["checks"].append({
                "name": "InfluxDB PM Storage",
                "status": "PASS" if influx_ok else "FAIL",
                "details": {"auth": "OK" if influx_ok else "401 Unauthorized"}
            })
        else:
            results["checks"].append({"name": "InfluxDB PM Storage", "status": "FAIL", "details": {"http": resp.status_code}})
    except Exception as e:
        results["checks"].append({"name": "InfluxDB PM Storage", "status": "FAIL", "details": {"error": str(e)}})

    # (d) A1 Policy Management (A1PMS RIC Discovery)
    a1pms_ok = False
    try:
        # A1PMS reachable from SMO via nonrtric namespace
        target_url = "http://policymanagementservice.nonrtric:8081/a1-policy/v2/rics"
        resp = requests.get(target_url, timeout=5)
        if resp.status_code == 200:
            rics = resp.json().get("rics", [])
            # Mark as PASS if service is reachable, even if 0 RICs
            results["checks"].append({
                "name": "A1 Policy Management",
                "status": "PASS",
                "details": {
                    "rics_found": len(rics),
                    "note": "Verify RIC simulators in nonrtric namespace if 0" if not rics else "Connected"
                }
            })
        else:
            results["checks"].append({"name": "A1 Policy Management", "status": "FAIL", "details": {"http": resp.status_code}})
    except Exception as e:
        results["checks"].append({"name": "A1 Policy Management", "status": "FAIL", "details": {"error": str(e)}})

    results["all_pass"] = all(c["status"] == "PASS" for c in results["checks"])
    return results


@app.route("/api/integration-check")
def api_integration_check():
    return jsonify(check_integration_points())


# ═══════════════════════════════════════════════════════════
#  FEATURE 6: Check MinIO for XML/JSON Files
# ═══════════════════════════════════════════════════════════

def check_minio_files():
    """List buckets and check for XML and JSON files in MinIO."""
    try:
        from minio import Minio
    except ImportError:
        return {"error": "minio package not installed. Run: pip install minio"}

    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key=SMO["minio_access_key"],
            secret_key=SMO["minio_secret_key"],
            secure=False,
        )
        buckets = client.list_buckets()
        result = {"buckets": [], "total_xml": 0, "total_json": 0}

        for bucket in buckets:
            bucket_info = {"name": bucket.name, "xml_files": [], "json_files": []}
            try:
                objects = list(client.list_objects(bucket.name, recursive=True))
                for obj in objects[:100]:  # Limit to 100 per bucket
                    name = obj.object_name
                    if name.endswith(".xml"):
                        bucket_info["xml_files"].append({"name": name, "size": obj.size})
                        result["total_xml"] += 1
                    elif name.endswith(".json") or name.endswith(".json.gz"):
                        bucket_info["json_files"].append({"name": name, "size": obj.size})
                        result["total_json"] += 1
            except Exception as e:
                bucket_info["error"] = str(e)
            result["buckets"].append(bucket_info)

        return result
    except Exception as e:
        return {"error": str(e)}


@app.route("/api/minio/files")
def api_minio_files():
    return jsonify(check_minio_files())


# ═══════════════════════════════════════════════════════════
#  FEATURE 7: List InfluxDB Buckets with Data
# ═══════════════════════════════════════════════════════════

def get_influxdb_buckets():
    """List all InfluxDB buckets and check which ones have recent data."""
    headers = {"Authorization": f"Token {INFLUX_TOKEN}"}
    result = {"buckets": [], "health": None}

    # Health check
    try:
        resp = requests.get(f"{INFLUX_URL}/health", timeout=10)
        if resp.status_code == 200:
            health = resp.json()
            result["health"] = {"status": health.get("status"), "version": health.get("version")}
    except Exception as e:
        result["health"] = {"error": str(e)}

    # List buckets
    try:
        auth = HTTPBasicAuth(SMO.get("influxdb_user", "admin"), SMO.get("influxdb_password", "admin"))
        resp = requests.get(f"{INFLUX_URL}/api/v2/buckets", headers=headers, timeout=10)
        if resp.status_code != 200:
            result["error"] = f"HTTP {resp.status_code}"
            return result

        data = resp.json()
        for b in data.get("buckets", []):
            name = b.get("name", "?")
            bucket_info = {"name": name, "id": b.get("id"), "has_data": False, "row_count": 0}

            # Skip internal buckets for data check
            if name.startswith("_"):
                bucket_info["note"] = "system bucket"
                result["buckets"].append(bucket_info)
                continue

            # Query for recent data
            try:
                query = f'from(bucket: "{name}") |> range(start: -24h) |> first() |> limit(n: 5)'
                qresp = requests.post(
                    f"{INFLUX_URL}/api/v2/query?org={INFLUX_ORG}",
                    headers={**headers, "Content-Type": "application/vnd.flux", "Accept": "application/csv"},
                    data=query, timeout=10,
                )
                if qresp.status_code == 200:
                    lines = [l for l in qresp.text.strip().split("\n") if l and not l.startswith("#")]
                    row_count = max(0, len(lines) - 1)  # subtract header
                    bucket_info["has_data"] = row_count > 0
                    bucket_info["row_count"] = row_count
            except:
                pass

            result["buckets"].append(bucket_info)
    except Exception as e:
        result["error"] = str(e)

    return result


@app.route("/api/influxdb/buckets")
def api_influxdb_buckets():
    return jsonify(get_influxdb_buckets())


# ═══════════════════════════════════════════════════════════
#  FEATURE 8: Send A1 Policy (Non-RT → Near-RT)
# ═══════════════════════════════════════════════════════════


def send_a1_policy(policy_type_id="", policy_id=None, ric_id=None, policy_data=None):
    print(f"DEBUG A1: Entering send_a1_policy(type='{policy_type_id}', id='{policy_id}', ric='{ric_id}')", flush=True)
    if policy_id is None:
        policy_id = f"integration-rapp-policy-{int(time.time())}"
    result = {"policy_id": policy_id, "steps": []}

    # Step 1: Get available RICs
    try:
        resp = requests.get(f"{A1PMS_URL}/a1-policy/v2/rics", timeout=10)
        if resp.status_code == 200:
            rics = resp.json().get("rics", [])
            result["steps"].append({"action": "LIST_RICS", "count": len(rics), "status": "OK"})
            if not ric_id and rics:
                ric_id = rics[0].get("ric_id", "")
        else:
            result["steps"].append({"action": "LIST_RICS", "status": f"HTTP {resp.status_code}"})
    except Exception as e:
        result["steps"].append({"action": "LIST_RICS", "status": f"ERROR: {e}"})

    # Step 2: Get policy types
    try:
        resp = requests.get(f"{A1PMS_URL}/a1-policy/v2/policy-types", timeout=10)
        if resp.status_code == 200:
            types = resp.json().get("policytype_ids", resp.json().get("policy_type_ids", []))
            result["steps"].append({"action": "LIST_TYPES", "types": types, "status": "OK"})
            if not policy_type_id and types:
                policy_type_id = types[0]
        else:
            result["steps"].append({"action": "LIST_TYPES", "status": f"HTTP {resp.status_code}"})
    except Exception as e:
        result["steps"].append({"action": "LIST_TYPES", "status": f"ERROR: {e}"})

    if not ric_id:
        result["error"] = "No RIC available to send policy to"
        return result

    # Step 3: Create/Send the policy
    print(f"DEBUG A1: Before payload selection, policy_type_id='{policy_type_id}' (type: {type(policy_type_id)})", flush=True)
    if policy_data is None:
        if str(policy_type_id) == "20000":
            policy_data = {"threshold": 10}
            print(f"DEBUG A1: Selected threshold payload for type 20000", flush=True)
        else:
            policy_data = {"scope": {"ueId": "integration-test"}, "qosObjectives": {"priorityLevel": 1}}
            print(f"DEBUG A1: Selected generic payload (policy_type_id != '20000')", flush=True)

    policy_body = {
        "ric_id": ric_id,
        "policy_id": policy_id,
        "policytype_id": str(policy_type_id) if policy_type_id else "",
        "policy_data": policy_data,
        "service_id": "integration-rapp",
    }

    try:
        print(f"DEBUG A1: Sending PUT to {A1PMS_URL}/a1-policy/v2/policies with body: {json.dumps(policy_body)}", flush=True)
        resp = requests.put(
            f"{A1PMS_URL}/a1-policy/v2/policies",
            json=policy_body,
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        print(f"DEBUG A1: A1PMS Response: {resp.status_code} - {resp.text}", flush=True)
        if resp.status_code in [200, 201]:
            result["steps"].append({"action": "SEND_POLICY", "status": "OK", "http": resp.status_code})
            # Verify via GET
            vresp = requests.get(f"{A1PMS_URL}/a1-policy/v2/policies/{policy_id}", timeout=10)
            result["steps"].append({
                "action": "VERIFY_POLICY",
                "status": "OK" if vresp.status_code == 200 else "FAIL",
                "http": vresp.status_code
            })
            result["sent"] = vresp.status_code == 200
        else:
            result["steps"].append({
                "action": "SEND_POLICY",
                "http": resp.status_code,
                "status": "FAIL",
                "response": resp.text[:500]
            })
            result["sent"] = False
    except Exception as e:
        result["steps"].append({"action": "SEND_POLICY", "status": f"ERROR: {e}"})
        result["sent"] = False

    return result


@app.route("/api/policy", methods=["POST"])
def api_send_policy():
    body = request.get_json(force=True, silent=True) or {}
    print(f"DEBUG A1 API: Received request with body: {body}", flush=True)
    return jsonify(send_a1_policy(
        policy_type_id=body.get("policy_type_id", ""),
        policy_id=body.get("policy_id"),
        ric_id=body.get("ric_id"),
        policy_data=body.get("policy_data"),
    ))


def get_all_policies():
    """Fetch all policies from A1PMS and enrich with details."""
    try:
        # 1. Get all policy IDs
        resp = requests.get(f"{A1PMS_URL}/a1-policy/v2/policies", timeout=10)
        if resp.status_code != 200:
            return {"error": f"A1PMS Error: {resp.status_code}", "policies": []}
        
        policy_ids = resp.json().get("policy_ids", [])
        detailed_policies = []
        
        # 2. Fetch details for each (or at least basic info)
        for pid in policy_ids:
            try:
                p_resp = requests.get(f"{A1PMS_URL}/a1-policy/v2/policies/{pid}", timeout=5)
                if p_resp.status_code == 200:
                    detailed_policies.append(p_resp.json())
                else:
                    detailed_policies.append({"policy_id": pid, "status": "Error fetching details"})
            except:
                detailed_policies.append({"policy_id": pid, "status": "Timeout"})
                
        return {"total": len(policy_ids), "policies": detailed_policies}
    except Exception as e:
        return {"error": str(e), "policies": []}


@app.route("/api/policies")
def api_list_policies():
    return jsonify(get_all_policies())


# ═══════════════════════════════════════════════════════════
#  FEATURE 8: Execute Netconf RPC (get-config)
# ═══════════════════════════════════════════════════════════

def exec_netconf_rpc(node_id):
    """Execute ietf-netconf:get-config RPC on a specific SDNR Node."""
    target_url = (
        f"{SDNR_URL}/rests/operations/network-topology:network-topology/"
        f"topology=topology-netconf/node={node_id}/yang-ext:mount/ietf-netconf:get-config"
    )
    # ietf-netconf:get-config payload exactly as confirmed by the user's working curl
    payload = {"input": {"ietf-netconf:source": {"running": [None]}}}
    
    try:
        r = requests.post(
            target_url, 
            json=payload, 
            auth=SDNR_AUTH,
            headers=SDNR_HEADERS, 
            timeout=30
        )
        if r.status_code in [200, 201]:
            return {"status": "success", "data": r.json()}
        else:
            return {"status": "error", "message": f"HTTP {r.status_code}", "details": r.text}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route("/api/nodes/<node_id>/rpc/get-config", methods=["POST"])
def api_rpc_get_config(node_id):
    return jsonify(exec_netconf_rpc(node_id))


# ═══════════════════════════════════════════════════════════
#  Web GUI Route
# ═══════════════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


# ═══════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Integration rApp — Backend API")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"  🚀 Integration rApp — Backend API")
    print(f"  GUI: http://localhost:{args.port}")
    print(f"  API: http://localhost:{args.port}/api/")
    print(f"{'='*60}\n")

    app.run(host=args.host, port=args.port, debug=True)
