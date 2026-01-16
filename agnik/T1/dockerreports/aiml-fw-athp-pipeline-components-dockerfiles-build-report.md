### aiml-fw-athp-pipeline-components Dockerfiles build verification (linux/amd64)

**Scope**
- All builds are successful after fixes

**Discovered Dockerfiles**
- `components/feature_extraction/feature_extraction/Dockerfile`
- `components/model_storage/model_storage/Dockerfile`
- `components/model_training/model_training/Dockerfile`

**Build commands**
```bash
# Feature extraction component
docker build -t aiml-feature-extraction:test components/feature_extraction/feature_extraction

# Model storage component
docker build -t aiml-model-storage:test components/model_storage/model_storage

# Model training component
docker build -t aiml-model-training:test components/model_training/model_training
```

**Issues Found and Fixed**
1. **model_storage/Dockerfile**: Removed `COPY runtime-requirements.txt runtime-requirements.txt` line as the file doesn't exist. The requirements are already specified in the RUN command.
2. **model_training/Dockerfile**: Removed `COPY runtime-requirements.txt runtime-requirements.txt` line as the file doesn't exist. The requirements are already specified in the RUN command.

**Results**
- aiml-feature-extraction:test — SUCCESS (149.9s build time)
- aiml-model-storage:test — SUCCESS (31.5s build time) - Fixed missing runtime-requirements.txt
- aiml-model-training:test — SUCCESS (311.2s build time) - Fixed missing runtime-requirements.txt

**Summary**
- Total Dockerfiles tested: 3
- Successful builds: 3
- Failed builds: 0 (after fixes)
- Issues fixed: 2 (both related to missing runtime-requirements.txt files)
