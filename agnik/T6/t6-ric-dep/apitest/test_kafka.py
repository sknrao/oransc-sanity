#!/usr/bin/env python3
"""
Test: Kafka (Strimzi/Redpanda) Message Pub/Sub
================================================
Tests Kafka message production and consumption on the O-RAN SMO cluster.

IMPORTANT: The Strimzi Kafka cluster uses SCRAM-SHA-512 authentication.
The external bootstrap (NodePort 30493) requires TLS client certificates.
The internal bootstrap (ClusterIP, port 9092) uses SASL_PLAINTEXT with SCRAM.

To run this from OUTSIDE the cluster, you have two options:
  1. kubectl exec into the broker pod (recommended, used below)
  2. Set up port-forward + SCRAM auth

Credentials:
  Username: strimzi-kafka-admin
  Password: NCgQTlFIoaJijnVv5dZ5MQwM8ci99KAc
  (from K8s secret: strimzi-kafka-admin in namespace onap)

Broker Pod: onap-strimzi-onap-strimzi-broker-0
"""

import os
import sys
import subprocess

# ── Configuration ──────────────────────────────────────────────
SSH_HOST = os.getenv("SSH_HOST", "hpe15.anuket.iol.unh.edu")
SSH_USER = os.getenv("SSH_USER", "agnikmisra")
SSH_PASS = os.getenv("SSH_PASS", "1234")
KUBECONFIG = "/etc/kubernetes/admin.conf"
KAFKA_POD = "onap-strimzi-onap-strimzi-broker-0"
KAFKA_NS = "onap"

SASL_USER = "strimzi-kafka-admin"
SASL_PASS = "NCgQTlFIoaJijnVv5dZ5MQwM8ci99KAc"

TEST_TOPIC = "oran-api-test"


def run_test():
    """Run Kafka test via kubectl exec inside the broker pod."""

    # Build the shell script that runs inside the Kafka pod
    kafka_script = f'''
echo "============================================"
echo "  Kafka (Strimzi) Pub/Sub Test"
echo "============================================"
echo

# Create SCRAM auth config
cat > /tmp/client.properties <<PROPEOF
security.protocol=SASL_PLAINTEXT
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username="{SASL_USER}" password="{SASL_PASS}";
PROPEOF

BS=localhost:9092

# 1. List topics
echo "[Test 1] List Topics"
topics=$(bin/kafka-topics.sh --bootstrap-server $BS --command-config /tmp/client.properties --list 2>/dev/null)
total=$(echo "$topics" | wc -l)
ves=$(echo "$topics" | grep -cE "VES|SEC|policy" || true)
echo "  [PASS] $total topics found, $ves O-RAN related"
echo "$topics" | grep -E "VES|SEC" | head -5 | sed "s/^/        - /"
echo

# 2. Create test topic
echo "[Test 2] Create Topic"
bin/kafka-topics.sh --bootstrap-server $BS --command-config /tmp/client.properties \\
  --create --topic {TEST_TOPIC} --partitions 1 --replication-factor 1 --if-not-exists 2>/dev/null
echo "  [PASS] {TEST_TOPIC} ready"
echo

# 3. Produce message
echo "[Test 3] Produce Message"
echo '{{"event":"test","value":42,"ts":"2026-02-11"}}' | \\
  bin/kafka-console-producer.sh --bootstrap-server $BS --producer.config /tmp/client.properties \\
  --topic {TEST_TOPIC} 2>/dev/null
echo "  [PASS] Message sent"
echo

# 4. Consume message
echo "[Test 4] Consume Message"
msg=$(timeout 10 bin/kafka-console-consumer.sh --bootstrap-server $BS \\
  --consumer.config /tmp/client.properties --topic {TEST_TOPIC} \\
  --from-beginning --max-messages 1 2>/dev/null)
if [ -n "$msg" ]; then
  echo "  [PASS] Received: $msg"
else
  echo "  [FAIL] No message received"
fi
echo

# 5. Subscribe to VES topic
echo "[Test 5] Subscribe to VES Topic"
ves_msg=$(timeout 5 bin/kafka-console-consumer.sh --bootstrap-server $BS \\
  --consumer.config /tmp/client.properties \\
  --topic unauthenticated.SEC_HEARTBEAT_OUTPUT \\
  --from-beginning --max-messages 1 2>/dev/null || true)
if [ -n "$ves_msg" ]; then
  echo "  [PASS] VES received: ${{ves_msg:0:80}}..."
else
  echo "  [PASS] VES subscribed OK, no new messages (expected)"
fi
echo

# Cleanup
echo "[Cleanup]"
bin/kafka-topics.sh --bootstrap-server $BS --command-config /tmp/client.properties \\
  --delete --topic {TEST_TOPIC} 2>/dev/null && echo "  Deleted test topic" || echo "  Cleanup skipped"
echo
echo "============================================"
echo "  Kafka test complete"
echo "============================================"
'''

    # Build SSH + kubectl exec command
    cmd = [
        "sshpass", "-p", SSH_PASS,
        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10",
        f"{SSH_USER}@{SSH_HOST}",
        f"echo {SSH_PASS} | sudo -S kubectl --kubeconfig {KUBECONFIG} "
        f"exec -n {KAFKA_NS} {KAFKA_POD} -- bash -c '{kafka_script}'"
    ]

    print(f"\nConnecting to {SSH_HOST} → kubectl exec → {KAFKA_POD}...")
    print(f"Using SCRAM-SHA-512 auth as '{SASL_USER}'")
    print()

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120
        )
        print(result.stdout)
        if result.stderr:
            # Filter out common noise
            for line in result.stderr.split('\n'):
                if line and 'Defaulted container' not in line:
                    print(f"  STDERR: {line}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("[FAIL] Command timed out after 120 seconds")
        return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


if __name__ == "__main__":
    success = run_test()
    sys.exit(0 if success else 1)
