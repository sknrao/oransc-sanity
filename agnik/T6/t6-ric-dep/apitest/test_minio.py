#!/usr/bin/env python3
"""
Test: MinIO S3 API Data Collection
===================================
Tests MinIO object storage via S3-compatible API.

MinIO S3 API (port 9000) is ClusterIP-only, but exposed via
kubectl port-forward on the server (hpe15).

Prerequisites:
  Run on hpe15 first:
    sudo kubectl --kubeconfig /etc/kubernetes/admin.conf \
      port-forward -n smo svc/minio 9000:9000 --address=0.0.0.0 &

Then set: MINIO_ENDPOINT=hpe15.anuket.iol.unh.edu:9000

Credentials: admin / adminadmin
"""

import os
import sys
import json
from io import BytesIO

try:
    from minio import Minio
    from minio.error import S3Error
except ImportError:
    print("ERROR: 'minio' package not installed. Run: pip install minio")
    sys.exit(1)

# ── Configuration ──────────────────────────────────────────────
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "hpe15.anuket.iol.unh.edu:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "adminadmin")
MINIO_SECURE = False

TEST_BUCKET = "test-api-bucket"
TEST_OBJECT = "test-data.json"
TEST_DATA = {"message": "Hello from API test", "timestamp": "2026-02-11"}

def print_result(test_name, passed, detail=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  [{status}] {test_name}" + (f" — {detail}" if detail else ""))

def run_tests():
    results = []

    print(f"\n{'='*60}")
    print(f"  MinIO S3 API Test — {MINIO_ENDPOINT}")
    print(f"{'='*60}\n")

    try:
        client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY,
                       secret_key=MINIO_SECRET_KEY, secure=MINIO_SECURE)
    except Exception as e:
        print(f"[FAIL] Cannot connect to MinIO: {e}")
        return False

    # Test 1: List buckets
    try:
        buckets = client.list_buckets()
        names = [b.name for b in buckets]
        print_result("List Buckets", True, f"Found {len(buckets)}: {names}")
        results.append(True)
    except Exception as e:
        print_result("List Buckets", False, str(e))
        results.append(False)

    # Test 2: Create bucket
    try:
        if not client.bucket_exists(TEST_BUCKET):
            client.make_bucket(TEST_BUCKET)
            print_result("Create Bucket", True, f"Created '{TEST_BUCKET}'")
        else:
            print_result("Create Bucket", True, f"'{TEST_BUCKET}' already exists")
        results.append(True)
    except Exception as e:
        print_result("Create Bucket", False, str(e))
        results.append(False)

    # Test 3: Upload object
    try:
        data = json.dumps(TEST_DATA).encode('utf-8')
        client.put_object(TEST_BUCKET, TEST_OBJECT, BytesIO(data), len(data),
                          content_type="application/json")
        print_result("Upload Object", True, f"'{TEST_OBJECT}' ({len(data)} bytes)")
        results.append(True)
    except Exception as e:
        print_result("Upload Object", False, str(e))
        results.append(False)

    # Test 4: List objects
    try:
        objects = list(client.list_objects(TEST_BUCKET))
        print_result("List Objects", True, f"{[o.object_name for o in objects]}")
        results.append(True)
    except Exception as e:
        print_result("List Objects", False, str(e))
        results.append(False)

    # Test 5: Download & verify
    try:
        resp = client.get_object(TEST_BUCKET, TEST_OBJECT)
        downloaded = json.loads(resp.read().decode('utf-8'))
        resp.close(); resp.release_conn()
        match = downloaded == TEST_DATA
        print_result("Download & Verify", match, f"Match: {match} — {downloaded}")
        results.append(match)
    except Exception as e:
        print_result("Download & Verify", False, str(e))
        results.append(False)

    # Test 6: Object stat
    try:
        stat = client.stat_object(TEST_BUCKET, TEST_OBJECT)
        print_result("Object Stat", True,
                     f"Size: {stat.size}B, Type: {stat.content_type}, Modified: {stat.last_modified}")
        results.append(True)
    except Exception as e:
        print_result("Object Stat", False, str(e))
        results.append(False)

    # Test 7: Delete object
    try:
        client.remove_object(TEST_BUCKET, TEST_OBJECT)
        print_result("Delete Object", True)
        results.append(True)
    except Exception as e:
        print_result("Delete Object", False, str(e))
        results.append(False)

    # Test 8: Delete bucket
    try:
        client.remove_bucket(TEST_BUCKET)
        print_result("Delete Bucket", True)
        results.append(True)
    except Exception as e:
        print_result("Delete Bucket", False, str(e))
        results.append(False)

    passed = sum(results)
    total = len(results)
    print(f"\n{'─'*60}")
    print(f"  MinIO Results: {passed}/{total} tests passed")
    print(f"{'─'*60}\n")
    return all(results)


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
