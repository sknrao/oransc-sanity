#!/usr/bin/env python3
"""
Integration rApp — CLI
========================
Command-line interface for all 8 Integration rApp features.

Usage:
    python cli.py nodes                      # 1. List SDNR nodes
    python cli.py reset S1-B12-C1            # 2. Reset a node
    python cli.py topics                     # 3. List Kafka topics
    python cli.py message pmreports          # 4. Latest message
    python cli.py integration               # 5. Check 3 integration points
    python cli.py minio                      # 6. Check MinIO files
    python cli.py buckets                    # 7. List InfluxDB buckets
    python cli.py policy                     # 8. Send A1 policy
    python cli.py all                        # Run all checks (1,3,5,7)
"""

import sys
import json
import argparse

# Reuse all backend functions
from backend import (
    get_sdnr_nodes, reset_node,
    get_kafka_topics, get_latest_message,
    check_integration_points,
    check_minio_files,
    get_influxdb_buckets,
    send_a1_policy,
)

# ANSI colors
G = "\033[32m"  # green
R = "\033[31m"  # red
Y = "\033[33m"  # yellow
C = "\033[36m"  # cyan
B = "\033[1m"   # bold
X = "\033[0m"   # reset


def section(title):
    print(f"\n{B}{C}{'═'*60}{X}")
    print(f"{B}{C}  {title}{X}")
    print(f"{B}{C}{'═'*60}{X}")


def status(label, ok, detail=""):
    icon = f"{G}✅ PASS{X}" if ok else f"{R}❌ FAIL{X}"
    d = f"  → {detail}" if detail else ""
    print(f"  {label:<45} {icon}{d}")


def cmd_nodes(_):
    section("1. Connected Nodes (SDNR)")
    data = get_sdnr_nodes()
    if "error" in data:
        status("SDNR RESTCONF", False, data["error"])
        return
    status("SDNR Nodes", True, f"{data['connected']} connected / {data['total']} total")
    for n in data["nodes"]:
        icon = f"{G}●{X}" if n["status"] == "connected" else f"{R}●{X}"
        print(f"    {icon} {n['node_id']} — {n['status']} ({n['host']}:{n['port']})")


def cmd_reset(args):
    section(f"2. Reset Node: {args.cell_id}")
    data = reset_node(args.cell_id)
    for step in data.get("steps", []):
        ok = step.get("status") == "OK"
        detail = step.get("state", step.get("http", ""))
        status(f"  {step['action']}", ok, str(detail))
    if data.get("final_state"):
        print(f"\n  Final state: {B}{data['final_state']}{X}")


def cmd_topics(_):
    section("3. Kafka Topics")
    data = get_kafka_topics()
    if "error" in data:
        status("Kafka", False, data["error"])
        return
    status("Topic listing", True, f"{data['total']} topics via {data.get('method','?')}")
    has_msgs = [t for t in data["topics"] if t.get("has_messages")]
    print(f"\n  Topics with data ({len(has_msgs)}):")
    for t in data["topics"][:20]:
        size = t.get("size_bytes", 0)
        icon = f"{G}●{X}" if t.get("has_messages") else f"{Y}○{X}"
        size_str = f"{size/1024:.0f} KB" if size > 0 else "empty"
        print(f"    {icon} {t['name']:<55} {size_str}")


def cmd_message(args):
    section(f"4. Latest Message: {args.topic}")
    data = get_latest_message(args.topic)
    if "error" in data:
        status("Message", False, data["error"])
        return
    status("Message received", True, f"via {data.get('method','?')}")
    value = data.get("value")
    if isinstance(value, dict):
        print(f"\n{json.dumps(value, indent=2)}")
    else:
        print(f"\n{value}")


def cmd_integration(_):
    section("5. Integration Points Check")
    data = check_integration_points()
    for check in data["checks"]:
        ok = check["status"] == "PASS"
        detail = ""
        if "sdnr_nodes" in check.get("details", {}):
            detail = f"{check['details']['sdnr_nodes']} SDNR nodes"
        elif "count" in check.get("details", {}):
            detail = f"{check['details']['count']} found"
        status(check["name"], ok, detail)

    overall = data.get("all_pass", False)
    icon = f"{G}ALL PASS{X}" if overall else f"{R}SOME FAILED{X}"
    print(f"\n  Overall: {B}{icon}{X}")


def cmd_minio(_):
    section("6. MinIO Files")
    data = check_minio_files()
    if "error" in data:
        status("MinIO S3", False, data["error"])
        return
    status("MinIO connected", True, f"XML: {data['total_xml']}, JSON: {data['total_json']}")
    for b in data["buckets"]:
        xml_c = len(b.get("xml_files", []))
        json_c = len(b.get("json_files", []))
        print(f"    📦 {b['name']}: {xml_c} XML, {json_c} JSON")


def cmd_buckets(_):
    section("7. InfluxDB Buckets")
    data = get_influxdb_buckets()
    if data.get("health"):
        h = data["health"]
        status("InfluxDB Health", h.get("status") == "pass",
               f"v{h.get('version', '?')}")
    for b in data.get("buckets", []):
        has = b.get("has_data", False)
        icon = f"{G}●{X}" if has else f"{Y}○{X}"
        rows = b.get("row_count", 0)
        note = b.get("note", f"{rows} rows")
        print(f"    {icon} {b['name']:<30} {note}")


def cmd_policy(_):
    section("8. Send A1 Policy")
    data = send_a1_policy()
    for step in data.get("steps", []):
        ok = step.get("status") == "OK"
        status(f"  {step['action']}", ok, str(step.get("http", step.get("count", ""))))
    sent = data.get("sent", False)
    icon = f"{G}SENT{X}" if sent else f"{R}NOT SENT{X}"
    print(f"\n  Policy: {B}{icon}{X} (ID: {data.get('policy_id', '?')})")


def cmd_all(_):
    """Run all read-only checks (1, 3, 5, 7)."""
    cmd_nodes(_)
    cmd_topics(_)
    cmd_integration(_)
    cmd_buckets(_)
    print(f"\n{B}{'='*60}{X}")
    print(f"{B}  Integration rApp — All checks complete{X}")
    print(f"{B}{'='*60}{X}\n")


def main():
    parser = argparse.ArgumentParser(
        description="O-RAN Integration rApp — CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    sub.add_parser("nodes", help="1. List connected SDNR nodes")

    p_reset = sub.add_parser("reset", help="2. Reset a cell node")
    p_reset.add_argument("cell_id", help="Cell ID to reset (e.g. S1-B12-C1)")

    sub.add_parser("topics", help="3. List Kafka topics with messages")

    p_msg = sub.add_parser("message", help="4. Show latest message from a topic")
    p_msg.add_argument("topic", help="Topic name (e.g. pmreports)")

    sub.add_parser("integration", help="5. Check 3 integration points")
    sub.add_parser("minio", help="6. Check MinIO for XML/JSON files")
    sub.add_parser("buckets", help="7. List InfluxDB buckets with data")
    sub.add_parser("policy", help="8. Send A1 policy")
    sub.add_parser("all", help="Run all read-only checks")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "nodes": cmd_nodes,
        "reset": cmd_reset,
        "topics": cmd_topics,
        "message": cmd_message,
        "integration": cmd_integration,
        "minio": cmd_minio,
        "buckets": cmd_buckets,
        "policy": cmd_policy,
        "all": cmd_all,
    }

    print(f"\n{B}O-RAN Integration rApp — CLI{X}")
    commands[args.command](args)


if __name__ == "__main__":
    main()
