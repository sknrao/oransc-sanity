# RIC Platform Utils Dockerfiles Build Report

## Repository Information
- **Repository**: [ric-plt-utils](https://github.com/o-ran-sc/ric-plt-utils)
- **Description**: Platform utility projects including Metrics Gateway xAPP (MG-xAPP)
- **Analysis Date**: January 2025
- **Total Dockerfiles Found**: 1

## Summary
The ric-plt-utils repository contains a single Dockerfile for the MG-xAPP (Metrics Gateway xAPP) project. The main issues encountered were related to outdated package repositories and missing dependencies. The Dockerfile uses a multi-stage build approach but fails due to package availability issues.

## Dockerfiles Analysis

### 1. mgxapp/Dockerfile
- **Purpose**: Build container for the Metrics Gateway xAPP (munchkin)
- **Base Images**: `ubuntu:18.04` (build stage), `ubuntu:20.04` (runtime stage)
- **Status**: ❌ **Build Fails** - Package availability issues

#### Issues Found and Fixes Applied:

**Issue 1: Dockerfile Casing Warning**
- **Problem**: `FROM ubuntu:18.04 as buildenv` uses lowercase 'as' instead of uppercase 'AS'
- **Error**: `FromAsCasing: 'as' and 'FROM' keywords' casing do not match`
- **Fix Applied**: Changed `FROM ubuntu:18.04 as buildenv` to `FROM ubuntu:18.04 AS buildenv`
- **Status**: ✅ **Fixed**

**Issue 2: Outdated Package Repository URLs**
- **Problem**: Dockerfile references Debian Stretch repositories which are deprecated
- **Error**: `404 Not Found` when trying to download packages from stretch repositories
- **Fix Applied**: Updated repository URLs from `stretch` to `bullseye`
- **Status**: ✅ **Fixed** (but packages still not available)

**Issue 3: Package Availability Issues**
- **Problem**: Required packages (mdclog, rmr, ricxfcpp) are not available in the updated repositories
- **Error**: `404 Not Found` when downloading packages from bullseye repositories
- **Root Cause**: The specific package versions and architectures may not be available in the target repositories
- **Status**: ❌ **Not Fixed** - Requires package repository investigation or alternative approach

**Issue 4: Base Image Version Mismatch**
- **Problem**: Build stage uses Ubuntu 18.04 while runtime stage uses Ubuntu 20.04
- **Fix Applied**: Updated runtime stage to use Ubuntu 20.04 for consistency
- **Status**: ✅ **Fixed**

#### Build Results:
- **Initial Build**: Failed due to repository access issues
- **After Repository URL Fix**: Failed due to package availability issues
- **Final Status**: Build fails at package download stage

## Technical Details

### Repository Structure:
```
ric-plt-utils/
├── mgxapp/                    # Metrics Gateway xAPP project
│   ├── Dockerfile            # Main Dockerfile
│   ├── src/                  # Source code
│   ├── lib/                  # Library code
│   ├── test/                 # Test files
│   ├── xapp_config.json      # Configuration file
│   └── README                # Project documentation
├── docs/                     # Documentation
└── README                    # Repository documentation
```

### Dependencies:
- **mdclog**: Logging library (version 0.0.4)
- **rmr**: RIC Message Router (version 4.1.4)
- **ricxfcpp**: RIC xAPP Framework C++ (version 2.1.0)
- **libcurl**: HTTP client library
- **CMake**: Build system

### Build Process:
1. **Build Stage**:
   - Installs build dependencies (git, cmake, make, g++, wget, curl, libcurl dev packages)
   - Downloads and installs development packages (mdclog-dev, rmr-dev, ricxfcpp-dev)
   - Builds the munchkin utility using CMake
   - Installs the binary to `/usr/local/bin`

2. **Runtime Stage**:
   - Installs runtime dependencies (wget, curl, libcurl runtime packages)
   - Downloads and installs runtime packages (mdclog, rmr, ricxfcpp)
   - Copies the built binary from the build stage
   - Sets up configuration and working directory
   - Runs the munchkin utility with configuration file

## Recommendations

### Immediate Actions:
1. **Investigate Package Availability**: Check the O-RAN-SC package repositories to determine which packages are actually available for different Debian versions.

2. **Update Package Versions**: Consider updating to newer versions of the dependencies that are available in the target repositories.

3. **Alternative Package Sources**: Explore alternative ways to obtain the required packages, such as:
   - Building from source
   - Using different package repositories
   - Using pre-built Docker images with the dependencies

### Long-term Improvements:
1. **Modernize Base Images**: Consider using more recent Ubuntu versions (22.04 LTS) for better security and support.

2. **Simplify Dependencies**: Evaluate if all dependencies are necessary and consider alternatives.

3. **Add Health Checks**: Implement health checks for the container to ensure the service is running properly.

4. **Security Scanning**: Integrate security scanning tools in the CI pipeline.

5. **Multi-architecture Support**: Consider adding support for different architectures (ARM64, etc.).

## Alternative Approaches

### Option 1: Build Dependencies from Source
Instead of downloading pre-built packages, build the dependencies from source in the Dockerfile.

### Option 2: Use Different Base Images
Consider using base images that already have the required dependencies installed.

### Option 3: Package Repository Investigation
Investigate the O-RAN-SC package repositories to find the correct URLs and versions for the required packages.

## Conclusion

The ric-plt-utils repository contains a well-structured Dockerfile with a multi-stage build approach. The main issue is the unavailability of the required packages in the target repositories. The Dockerfile syntax and structure are correct, but the dependency management needs to be addressed.

The MG-xAPP project appears to be a metrics gateway that listens for RMR messages and forwards data to collectors, which is a valuable component in the RIC platform ecosystem.

## Files Modified:
- `mgxapp/Dockerfile`: 
  - Fixed casing: `FROM ubuntu:18.04 as buildenv` → `FROM ubuntu:18.04 AS buildenv`
  - Updated repository URLs: `stretch` → `bullseye`
  - Updated runtime base image: `ubuntu:18.04` → `ubuntu:20.04`

## Build Status:
- **Dockerfile Syntax**: ✅ Valid
- **Base Images**: ✅ Updated to supported versions
- **Repository URLs**: ✅ Updated to supported repositories
- **Package Availability**: ❌ Packages not found in target repositories
- **Overall Status**: ❌ **Build Fails** - Package availability issues need resolution
