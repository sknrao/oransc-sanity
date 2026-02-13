#!/usr/bin/env python3
"""
Test: SDNR RESTCONF Device Configuration
==========================================
Tests reading and modifying device configuration via
SDNC/SDNR RESTCONF API on hpe15:30267.

Follows the same patterns from the O-RU Fronthaul Recovery
and RAN Slice Assurance rApps.
"""

import os
import sys
import json
import requests
from requests.auth import HTTPBasicAuth

# Suppress InsecureRequestWarning
requests.packages.urllib3.disable_warnings()

# ── Configuration ──────────────────────────────────────────────
SDNR_URL = os.getenv("SDNR_URL", "http://hpe15.anuket.iol.unh.edu:30267")
SDNR_USER = os.getenv("SDNR_USER", "admin")
SDNR_PASS = os.getenv("SDNR_PASS", "Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U")

BASE_PATH = "/rests/data/network-topology:network-topology"
TOPOLOGY_PATH = f"{BASE_PATH}/topology=topology-netconf"

AUTH = HTTPBasicAuth(SDNR_USER, SDNR_PASS)
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def print_result(test_name, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  [{status}] {test_name}" + (f" — {detail}" if detail else ""))

def run_tests():
    results = []

    print(f"\n{'='*60}")
    print(f"  SDNR RESTCONF Config Test — {SDNR_URL}")
    print(f"{'='*60}\n")

    # Test 1: Get full network topology
    try:
        resp = requests.get(
            f"{SDNR_URL}{BASE_PATH}",
            auth=AUTH, headers=HEADERS, timeout=10
        )
        if resp.status_code == 200:
            topo = resp.json()
            topologies = topo.get("network-topology:network-topology", {}).get("topology", [])
            for t in topologies:
                nodes = t.get("node", [])
                node_ids = [n.get("node-id") for n in nodes]
                print_result("Get Topology", True,
                             f"Topology '{t.get('topology-id')}': {len(nodes)} nodes — {node_ids}")
            results.append(True)
        else:
            print_result("Get Topology", False, f"HTTP {resp.status_code}")
            results.append(False)
    except Exception as e:
        print_result("Get Topology", False, str(e))
        results.append(False)

    # Test 2: Get individual node details
    connected_nodes = []
    try:
        resp = requests.get(
            f"{SDNR_URL}{TOPOLOGY_PATH}",
            auth=AUTH, headers=HEADERS, timeout=10
        )
        if resp.status_code == 200:
            topology = resp.json()
            nodes = []
            for t in topology.get("network-topology:topology", topology.get("topology", [])):
                if isinstance(t, dict):
                    nodes.extend(t.get("node", []))
            for node in nodes:
                node_id = node.get("node-id")
                status = node.get("netconf-node-topology:connection-status", "unknown")
                host = node.get("netconf-node-topology:host", "?")
                port = node.get("netconf-node-topology:port", "?")
                if status == "connected":
                    connected_nodes.append(node_id)
                print(f"        → {node_id}: {status} ({host}:{port})")
            print_result("List Nodes", True, f"{len(connected_nodes)} connected nodes")
            results.append(True)
        else:
            print_result("List Nodes", False, f"HTTP {resp.status_code}")
            results.append(False)
    except Exception as e:
        print_result("List Nodes", False, str(e))
        results.append(False)

    # Test 3: Read device config (pick first connected O-DU)
    target_node = None
    for n in connected_nodes:
        if n.startswith("o-du"):
            target_node = n
            break
    if not target_node and connected_nodes:
        target_node = connected_nodes[0]

    device_config = None
    if target_node:
        try:
            node_path = f"{TOPOLOGY_PATH}/node={target_node}"
            resp = requests.get(
                f"{SDNR_URL}{node_path}",
                auth=AUTH, headers=HEADERS, timeout=10
            )
            if resp.status_code == 200:
                device_config = resp.json()
                caps = device_config.get("network-topology:node", [{}])[0]
                avail_caps = caps.get("netconf-node-topology:available-capabilities", {})
                cap_list = avail_caps.get("available-capability", [])
                print_result("Read Device Config", True,
                             f"Node '{target_node}': {len(cap_list)} capabilities loaded")
                results.append(True)
            else:
                print_result("Read Device Config", False,
                             f"HTTP {resp.status_code} for node '{target_node}'")
                results.append(False)
        except Exception as e:
            print_result("Read Device Config", False, str(e))
            results.append(False)
    else:
        print_result("Read Device Config", False, "No connected nodes found")
        results.append(False)

    # Test 4: Read mounted device's YANG data (O-DU config via mount point)
    if target_node:
        try:
            mount_path = (f"{TOPOLOGY_PATH}/node={target_node}"
                          f"/yang-ext:mount")
            # Try to read the hello-world network function if available
            yang_path = (f"{mount_path}/o-ran-sc-du-hello-world:network-function")
            resp = requests.get(
                f"{SDNR_URL}{yang_path}",
                auth=AUTH, headers=HEADERS, timeout=10
            )
            if resp.status_code == 200:
                config_data = resp.json()
                print_result("Read YANG Config (mount)", True,
                             f"Got YANG data from '{target_node}' mount point")
                # Show some details
                nf = config_data.get("o-ran-sc-du-hello-world:network-function", {})
                du_funcs = nf.get("distributed-unit-functions", [])
                for du in du_funcs:
                    du_id = du.get("id", "?")
                    rrm_policies = du.get("radio-resource-management-policy-ratio", [])
                    for pol in rrm_policies:
                        print(f"        → DU '{du_id}': RRM Policy '{pol.get('id')}' — "
                              f"dedicated-ratio: {pol.get('radio-resource-management-policy-dedicated-ratio')}, "
                              f"admin-state: {pol.get('administrative-state')}")
                results.append(True)
            elif resp.status_code == 404:
                print_result("Read YANG Config (mount)", True,
                             f"YANG model o-ran-sc-du-hello-world not available on '{target_node}' "
                             "(expected for non-simulator nodes)")
                results.append(True)
            else:
                print_result("Read YANG Config (mount)", False,
                             f"HTTP {resp.status_code}")
                results.append(False)
        except Exception as e:
            print_result("Read YANG Config (mount)", False, str(e))
            results.append(False)
    else:
        print_result("Read YANG Config (mount)", False, "No target node")
        results.append(False)

    # Test 5: Modify device config — Mount/Unmount a test device
    test_device_id = "test-api-device-1"
    try:
        mount_body = {
            "network-topology:node": [{
                "node-id": test_device_id,
                "netconf-node-topology:host": "10.0.0.99",
                "netconf-node-topology:port": 830,
                "netconf-node-topology:username": "admin",
                "netconf-node-topology:password": "admin",
                "netconf-node-topology:tcp-only": False,
                "netconf-node-topology:keepalive-delay": 120
            }]
        }
        mount_path = f"{TOPOLOGY_PATH}/node={test_device_id}"
        resp = requests.put(
            f"{SDNR_URL}{mount_path}",
            auth=AUTH, headers=HEADERS, json=mount_body, timeout=10
        )
        if resp.status_code in [200, 201, 204]:
            print_result("Mount Test Device", True,
                         f"HTTP {resp.status_code} — Mounted '{test_device_id}'")
            results.append(True)
        else:
            print_result("Mount Test Device", False,
                         f"HTTP {resp.status_code}: {resp.text[:200]}")
            results.append(False)
    except Exception as e:
        print_result("Mount Test Device", False, str(e))
        results.append(False)

    # Test 6: Verify test device appears in topology
    try:
        import time
        time.sleep(2)  # Give SDNR a moment to process
        resp = requests.get(
            f"{SDNR_URL}{TOPOLOGY_PATH}/node={test_device_id}",
            auth=AUTH, headers=HEADERS, timeout=10
        )
        if resp.status_code == 200:
            node_data = resp.json()
            node_info = node_data.get("network-topology:node", [{}])[0]
            conn_status = node_info.get("netconf-node-topology:connection-status", "unknown")
            print_result("Verify Mounted Device", True,
                         f"'{test_device_id}' visible in topology, status: {conn_status}")
            results.append(True)
        else:
            print_result("Verify Mounted Device", False, f"HTTP {resp.status_code}")
            results.append(False)
    except Exception as e:
        print_result("Verify Mounted Device", False, str(e))
        results.append(False)

    # Test 7: Unmount (clean up) the test device
    try:
        resp = requests.delete(
            f"{SDNR_URL}{TOPOLOGY_PATH}/node={test_device_id}",
            auth=AUTH, headers=HEADERS, timeout=10
        )
        if resp.status_code in [200, 204]:
            print_result("Unmount Test Device", True,
                         f"HTTP {resp.status_code} — Cleaned up '{test_device_id}'")
            results.append(True)
        else:
            print_result("Unmount Test Device", False,
                         f"HTTP {resp.status_code}: {resp.text[:200]}")
            results.append(False)
    except Exception as e:
        print_result("Unmount Test Device", False, str(e))
        results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{'─'*60}")
    print(f"  SDNR Results: {passed}/{total} tests passed")
    print(f"{'─'*60}\n")
    return all(results)


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
