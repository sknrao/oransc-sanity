FROM python:3.11-slim

# Install system dependencies (kubectl, sshpass)
RUN apt-get update && apt-get install -y \
    curl \
    sshpass \
    apt-transport-https \
    gnupg \
    && curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg \
    && echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | tee /etc/apt/sources.list.d/kubernetes.list \
    && apt-get update && apt-get install -y kubectl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .
RUN chmod +x kafka_consume.sh

# Expose Web GUI port
EXPOSE 5001

# Run the Flask server
CMD ["python", "backend.py", "--host", "0.0.0.0", "--port", "5001"]
