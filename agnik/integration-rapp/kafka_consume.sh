#!/bin/bash
# Helper script to consume one message from a Kafka topic.
# Usage: bash kafka_consume.sh <topic_name>

TOPIC=$1
if [ -z "$TOPIC" ]; then
    echo "Usage: $0 <topic_name>"
    exit 1
fi

KUBECONFIG=/etc/kubernetes/admin.conf
POD=onap-strimzi-onap-strimzi-broker-0
NS=onap
SASL_USER=strimzi-kafka-admin
SASL_PASS=G7ITDUBrDBRlZmSKtEMYt9sY2k1ZfBn2

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    SUDO="sudo"
fi

export KUBECONFIG=$KUBECONFIG

# 1. Setup client.properties inside the pod and get latest offsets
OFFSETS=$($SUDO kubectl exec -n $NS $POD -- bash -c "
echo -e 'security.protocol=SASL_PLAINTEXT
sasl.mechanism=SCRAM-SHA-512
sasl.jaas.config=org.apache.kafka.common.security.scram.ScramLoginModule required username=\"$SASL_USER\" password=\"$SASL_PASS\";
' > /tmp/client.properties
bin/kafka-get-offsets.sh --bootstrap-server localhost:9092 --topic $TOPIC --time -1 --command-config /tmp/client.properties 2>/dev/null
")

# 2. Parse the offset (find first partition with messages)
PARTITION=""
OFFSET=""
for line in $OFFSETS; do
    if [[ $line == ${TOPIC}:* ]]; then
        p=$(echo $line | cut -d: -f2)
        o=$(echo $line | cut -d: -f3)
        if [ -n "$o" ] && [ "$o" -gt 0 ]; then
            PARTITION=$p
            OFFSET=$o
            break
        fi
    fi
done

# 3. Consume the latest message
if [ -n "$OFFSET" ]; then
    TARGET_OFFSET=$((OFFSET - 1))
    $SUDO kubectl exec -n $NS $POD -- bash -c "
    timeout 10 bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --consumer.config /tmp/client.properties --topic $TOPIC --partition $PARTITION --offset $TARGET_OFFSET --max-messages 1 2>/dev/null
    "
else
    # Fallback if empty or offsets missing
    $SUDO kubectl exec -n $NS $POD -- bash -c "
    timeout 10 bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --consumer.config /tmp/client.properties --topic $TOPIC --from-beginning --max-messages 1 2>/dev/null
    "
fi
