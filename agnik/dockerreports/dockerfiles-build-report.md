### aiml-fw-aimlfw-dep Dockerfiles build verification (linux/amd64)

Scope
- All builds are successful

Discovered Dockerfiles
- `demos/example-rapp/rapp/Dockerfile`
- `demos/model-deployment/myapplication/Dockerfile`
- `tools/kubeflow/Dockerfile.pipeline`
- `tools/leofs/Dockerfile.leofs`

Build commands
```bash
# Example rApp
docker buildx build --platform linux/amd64 --load \
  -t aiml-example-rapp:dev demos/example-rapp/rapp

# Model deployment sample
docker buildx build --platform linux/amd64 --load \
  -t aiml-myapplication:dev demos/model-deployment/myapplication

# Kubeflow pipeline base
docker buildx build --platform linux/amd64 --load \
  -t aiml-kubeflow-pipeline:latest -f tools/kubeflow/Dockerfile.pipeline tools/kubeflow

# LeoFS helper (note: needs repo root as build context for COPY path)
docker buildx build --platform linux/amd64 --load \
  -t aiml-leofs:latest -f tools/leofs/Dockerfile.leofs .
```

Results
- aiml-example-rapp:dev — SUCCESS
- aiml-myapplication:dev — SUCCESS
- aiml-kubeflow-pipeline:latest — SUCCESS 
- aiml-leofs:latest — SUCCESS 
