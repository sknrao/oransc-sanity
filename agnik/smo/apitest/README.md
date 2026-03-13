# SMO API Testing Scripts

This directory contains standalone Python scripts to verify the core northbound APIs of the O-RAN Service Management and Orchestration (SMO) layer.

## Available Tests

| Script | Service | Port | Description |
|--------|---------|------|-------------|
| `test_influxdb.py` | InfluxDB | 32717 | Verifies health, buckets, and PM data read/write. |
| `test_kafka.py` | Kafka | 9092 | Tests topic listing, pub/sub, and VES topic subscription. |
| `test_sdnr.py` | SDNR | 30267 | Tests RESTCONF topology, node listing, and device mounting. |
| `test_minio.py` | MinIO | 9000 | Tests S3-compatible object storage (requires port-forward). |

## How to Run

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run All Tests
```bash
python3 run_all_tests.py
```

### 3. MinIO Port-Forwarding (Optional)
MinIO S3 API is ClusterIP-only. To test it, run this in a separate terminal on the server:
```bash
sudo kubectl --kubeconfig /etc/kubernetes/admin.conf \
  port-forward -n smo svc/minio 9000:9000 --address=0.0.0.0
```

## Results Archive
Previous test logs and detailed CRUD examples can be found in the `results_archive/` directory.
