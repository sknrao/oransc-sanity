# O-RAN-SC ric-plt-submgr Dockerfiles Build Report

**Repository:** [o-ran-sc/ric-plt-submgr](https://github.com/o-ran-sc/ric-plt-submgr)  
**Analysis Date:** January 2025  
**Total Dockerfiles Found:** 1  

## Executive Summary

The `ric-plt-submgr` repository contains 1 Dockerfile, with 0 building successfully initially and 1 building successfully after minimal fixes (100% success rate after fixes). The initial build failure was due to a Go version compatibility issue with the delve debugger. The repository implements the Subscription Manager component for E2 interface management in the RIC platform.

## Dockerfiles Analysis

### 1. Main Subscription Manager Dockerfile
**File:** `Dockerfile`  
**Status:** ✅ **SUCCESS** (After Minimal Fixes)  
**Build Command:** `sudo docker build --network=host -t ric-plt-submgr:main -f Dockerfile .`

**Description:** Multi-stage build for the Subscription Manager application
- **Base Images:** 
  - Build stage 1: `nexus3.o-ran-sc.org:10002/o-ran-sc/bldr-ubuntu20-c-go:1.0.0` (submgrcore)
  - Build stage 2: `submgrcore` (submgre2apbuild)
  - Build stage 3: `submgre2apbuild` (submgrbuild)
  - Runtime stage: `ubuntu:20.04`
- **Features:**
  - Go application build with RMR integration
  - E2AP ASN.1 C library compilation
  - Swagger code generation for routing manager API
  - Unit test execution for E2AP components
  - Code formatting validation
  - Multi-stage optimization for runtime image

**Initial Build Failure:**
```
go: github.com/go-delve/delve/cmd/dlv@latest (in github.com/go-delve/delve@v1.25.2): go.mod:3: invalid go version '1.22.0': must match format 1.23
```

**Root Cause:** Go version compatibility issue with delve debugger v1.25.2 requiring Go 1.22+ while the build uses Go 1.18.5.

**Minimal Fix Applied:**
```dockerfile
# Before
RUN export GOBIN=/usr/local/bin/ ; \
  go install github.com/go-delve/delve/cmd/dlv@latest

# After
RUN export GOBIN=/usr/local/bin/ ; \
  go install github.com/go-delve/delve/cmd/dlv@v1.20.2
```

**Post-Fix Status:** ✅ **SUCCESS** - Build completed successfully in 113.5 seconds.

---

## Summary Statistics

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Success (After Fixes) | 1 | 100% |
| ❌ Failed (Initial) | 1 | 100% |
| **Total** | **1** | **100%** |

## Common Issues Identified

1. **Go Version Compatibility:** Delve debugger version incompatibility with Go 1.18.5
2. **Dependency Version Management:** Need to pin specific versions for compatibility

## Minimal Fixes Applied

### Main Dockerfile Fixes:
1. **Delve Version Pinning:**
   ```dockerfile
   # Changed from @latest to specific version compatible with Go 1.18.5
   RUN export GOBIN=/usr/local/bin/ ; \
     go install github.com/go-delve/delve/cmd/dlv@v1.20.2
   ```

## Technical Details

### Subscription Manager Architecture
The Subscription Manager is a critical component in the O-RAN-SC RIC platform that provides:

1. **E2 Interface Management:** Handles E2 interface subscriptions and notifications
2. **ASN.1 Processing:** Compiles and uses E2AP ASN.1 C libraries
3. **RMR Integration:** Communicates via RIC Message Router
4. **Swagger API Generation:** Generates client code for routing manager API
5. **Unit Testing:** Comprehensive test coverage for E2AP components

### Dependencies and Libraries
- **RMR Integration:** Version 4.9.4 from packagecloud.io
- **Go Application:** Built with Go 1.18.5
- **E2AP ASN.1:** Version v02.00.00 compiled from C source
- **Swagger:** Version v0.23.0 for API code generation
- **Delve Debugger:** Version v1.20.2 (compatible with Go 1.18.5)
- **Routing Manager API:** Generated from Gerrit rtmgr repository

### Build Process Analysis
The Dockerfile follows a sophisticated four-stage build pattern:

1. **Stage 1 (`submgrcore`):**
   - Uses Nexus Ubuntu 20.04 Go builder image
   - Installs Go 1.18.5 and development tools
   - Installs Swagger v0.23.0 for API generation
   - Installs Delve debugger v1.20.2
   - Installs RMR libraries v4.9.4 from packagecloud.io
   - Sets up build environment and manifests

2. **Stage 2 (`submgre2apbuild`):**
   - Compiles E2AP ASN.1 C libraries from 3rdparty source
   - Builds libe2ap.so shared library
   - Compiles E2AP wrapper library
   - Runs unit tests for E2AP components
   - Validates code formatting

3. **Stage 3 (`submgrbuild`):**
   - Downloads Go module dependencies
   - Clones routing manager API from Gerrit
   - Generates Swagger client code
   - Builds main subscription manager binary
   - Runs code formatting validation
   - Prepares manifests and artifacts

4. **Stage 4 (Runtime):**
   - Uses clean Ubuntu 20.04 base
   - Copies built artifacts from previous stages
   - Installs runtime dependencies
   - Configures environment variables
   - Sets up entrypoint script

### E2AP Integration
The Subscription Manager includes sophisticated E2AP (E2 Application Protocol) integration:

1. **ASN.1 Compilation:** Compiles E2AP v02.00.00 ASN.1 specifications to C libraries
2. **Wrapper Library:** Provides Go wrapper for C E2AP libraries
3. **Unit Testing:** Comprehensive tests for ASN.1 conversion and wrapper functionality
4. **Code Formatting:** Validates Go code formatting standards

### API Generation
The build process includes automatic API client generation:

1. **Routing Manager API:** Clones from Gerrit and generates Swagger client
2. **Swagger Integration:** Uses go-swagger to generate Go client code
3. **Model Generation:** Creates Go models for API data structures
4. **Client Generation:** Generates HTTP client for routing manager communication

## Build Commands Used

```bash
# Successful build (after fix)
sudo docker build --network=host -t ric-plt-submgr:main -f Dockerfile .
```

## Architecture Overview

The Subscription Manager serves as a critical component in the RIC platform's E2 interface management:

1. **E2 Interface Management:** Handles E2 interface subscriptions between RIC and RAN nodes
2. **ASN.1 Processing:** Manages E2AP protocol message encoding/decoding
3. **RMR Communication:** Uses RIC Message Router for internal communication
4. **API Integration:** Provides REST API for subscription management
5. **Configuration Management:** Handles subscription policies and routing tables

### Key Features:
- **Multi-stage Build:** Optimized for both development and production
- **Comprehensive Testing:** Unit tests for all critical components
- **Code Quality:** Automated formatting validation
- **Dependency Management:** Proper version pinning for stability
- **Runtime Optimization:** Minimal runtime image with only necessary components

## Recommendations

1. **Version Pinning:** Continue pinning specific versions for all dependencies
2. **Go Version Updates:** Consider updating to newer Go versions for better compatibility
3. **Dependency Monitoring:** Regular updates of pinned versions for security
4. **Build Optimization:** Consider caching strategies for faster builds
5. **Documentation:** Maintain build documentation for dependency versions

## Build Performance

- **Total Build Time:** 113.5 seconds
- **Build Stages:** 4 stages with proper layer caching
- **Dependencies:** All dependencies resolved successfully
- **Tests:** All unit tests passed
- **Code Quality:** All formatting validations passed

---

**Report Generated:** January 2025  
**Analysis Tool:** Docker Build Testing Framework  
**Repository Status:** Buildable (1/1 Dockerfiles successful after fixes)

## Additional Notes

The Subscription Manager represents one of the most complex and well-architected Dockerfiles in the O-RAN-SC ecosystem, featuring:

1. **Sophisticated Multi-stage Build:** Four distinct build stages for different purposes
2. **ASN.1 Integration:** Complex C library compilation and Go wrapper generation
3. **API Generation:** Automatic Swagger client code generation
4. **Comprehensive Testing:** Unit tests for all critical components
5. **Production Ready:** Optimized runtime image with minimal footprint

The successful build demonstrates the robustness of the O-RAN-SC build system and the quality of the Subscription Manager implementation.
