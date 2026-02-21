#!/usr/bin/env python3
"""
Test: InfluxDB API Data Collection
====================================
Tests InfluxDB v2 API — health check, list buckets,
write test data, query data back, and cleanup.
"""

import os
import sys
import json
from datetime import datetime

try:
    from influxdb_client import InfluxDBClient, Point, WritePrecision
    from influxdb_client.client.write_api import SYNCHRONOUS
except ImportError:
    print("ERROR: 'influxdb-client' package not installed. Run: pip install influxdb-client")
    sys.exit(1)

# ── Configuration ──────────────────────────────────────────────
INFLUX_URL = os.getenv("INFLUX_URL", "http://hpe15.anuket.iol.unh.edu:31814")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "xjIEDWCopZtjSgJwkUBI0tWwqpCTXPvZ")
INFLUX_ORG = os.getenv("INFLUX_ORG", "est")
TEST_BUCKET = "pm-bucket"  # Use existing bucket

def print_result(test_name, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  [{status}] {test_name}" + (f" — {detail}" if detail else ""))

def run_tests():
    results = []

    print(f"\n{'='*60}")
    print(f"  InfluxDB API Test — {INFLUX_URL}")
    print(f"{'='*60}\n")

    # Connect
    try:
        client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    except Exception as e:
        print(f"[FAIL] Cannot connect to InfluxDB: {e}")
        return False

    # Test 1: Health Check
    try:
        health = client.health()
        healthy = health.status == "pass"
        print_result("Health Check", healthy,
                     f"Status: {health.status}, Version: {health.version}")
        results.append(healthy)
    except Exception as e:
        print_result("Health Check", False, str(e))
        results.append(False)

    # Test 2: List Buckets
    try:
        buckets_api = client.buckets_api()
        buckets = buckets_api.find_buckets()
        bucket_names = [b.name for b in buckets.buckets]
        print_result("List Buckets", True, f"Found {len(bucket_names)}: {bucket_names}")
        results.append(True)
    except Exception as e:
        print_result("List Buckets", False, str(e))
        results.append(False)

    # Test 3: List Organizations
    try:
        orgs_api = client.organizations_api()
        orgs = orgs_api.find_organizations()
        org_names = [o.name for o in orgs]
        print_result("List Organizations", True, f"Orgs: {org_names}")
        results.append(True)
    except Exception as e:
        print_result("List Organizations", False, str(e))
        results.append(False)

    # Test 4: Write Test Data
    try:
        write_api = client.write_api(write_options=SYNCHRONOUS)
        point = (
            Point("api_test")
            .tag("source", "python_test_script")
            .tag("test_run", "mentor_validation")
            .field("value", 42.0)
            .field("message", "Hello from InfluxDB API test")
            .time(datetime.utcnow(), WritePrecision.NS)
        )
        write_api.write(bucket=TEST_BUCKET, org=INFLUX_ORG, record=point)
        print_result("Write Data", True,
                     f"Wrote test point to '{TEST_BUCKET}' (measurement: api_test)")
        results.append(True)
    except Exception as e:
        print_result("Write Data", False, str(e))
        results.append(False)

    # Test 5: Query Data Back (Flux query)
    try:
        query_api = client.query_api()
        query = f'''
        from(bucket: "{TEST_BUCKET}")
          |> range(start: -1h)
          |> filter(fn: (r) => r._measurement == "api_test")
          |> filter(fn: (r) => r.source == "python_test_script")
          |> last()
        '''
        tables = query_api.query(query, org=INFLUX_ORG)
        records_found = 0
        for table in tables:
            for record in table.records:
                records_found += 1
                print(f"        → Field: {record.get_field()}, Value: {record.get_value()}, "
                      f"Time: {record.get_time()}")
        print_result("Query Data", records_found > 0,
                     f"Found {records_found} record(s) from api_test measurement")
        results.append(records_found > 0)
    except Exception as e:
        print_result("Query Data", False, str(e))
        results.append(False)

    # Test 6: Query existing PM data (if any)
    try:
        query_api = client.query_api()
        query = f'''
        from(bucket: "{TEST_BUCKET}")
          |> range(start: -24h)
          |> limit(n: 5)
        '''
        tables = query_api.query(query, org=INFLUX_ORG)
        total_records = sum(len(t.records) for t in tables)
        measurements = set()
        for table in tables:
            for record in table.records:
                measurements.add(record.get_measurement())
        if total_records > 0:
            print_result("Query Existing PM Data", True,
                         f"Found {total_records} records, measurements: {measurements}")
        else:
            print_result("Query Existing PM Data", True,
                         "No existing PM data yet (expected — pipeline not active)")
        results.append(True)
    except Exception as e:
        print_result("Query Existing PM Data", False, str(e))
        results.append(False)

    # Cleanup
    client.close()

    # Summary
    passed = sum(results)
    total = len(results)
    print(f"\n{'─'*60}")
    print(f"  InfluxDB Results: {passed}/{total} tests passed")
    print(f"{'─'*60}\n")
    return all(results)


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
