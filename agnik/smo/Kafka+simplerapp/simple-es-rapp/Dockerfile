FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir confluent-kafka requests
COPY simple_rapp.py .
CMD ["python", "-u", "simple_rapp.py"]
