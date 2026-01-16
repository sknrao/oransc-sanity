# Dockerfile Build Report for o-ran-sc/portal-nonrtric-controlpanel

**Repository:** [https://github.com/o-ran-sc/portal-nonrtric-controlpanel](https://github.com/o-ran-sc/portal-nonrtric-controlpanel)
**Date:** 2024-05-13

## 1. Repository Overview
- **Description:** O-RAN-SC Non-RT RIC Control Panel Web Application - Administrative and operator functions for Near-RT RIC through A1 API
- **Language:** TypeScript 75.9%, HTML 12.9%, SCSS 7.7%, JavaScript 1.0%, Dockerfile 1.0%, Shell 0.7%, Other 0.8%
- **Project Type:** O-RAN Non-RT RIC Control Panel Web Application
- **Lifecycle State:** Active development
- **Status:** Mirror of the portal/nonrtric-controlpanel repo
- **License:** Apache-2.0

## 2. Dockerfiles Discovered
**Result:** ✅ **2 DOCKERFILES FOUND**

The repository contains two Dockerfiles:
1. `./nonrtric-gateway/Dockerfile` - Spring Cloud Gateway backend service
2. `./webapp-frontend/Dockerfile` - Angular frontend application

## 3. Build Test Results

### 3.1 Overall Build Status
**Result:** ✅ **FULLY SUCCESSFUL (2/2)**

| Dockerfile | Status | Build Time | Issues Fixed |
|------------|--------|------------|--------------|
| `./nonrtric-gateway/Dockerfile` | ✅ SUCCESS | 28.4s | Maven build required |
| `./webapp-frontend/Dockerfile` | ✅ SUCCESS | 861.6s | None |

### 3.2 Detailed Analysis

#### 3.2.1 `./nonrtric-gateway/Dockerfile` ✅ SUCCESS

**Purpose:** Spring Cloud Gateway backend service for O-RAN Non-RT RIC Control Panel

**Base Image:** 
- Multi-stage build using `openjdk:17-jdk` for JRE creation
- Final stage: `debian:11-slim`

**Key Features:**
- Custom JRE creation using `jlink` for optimized container size
- Spring Boot 3.0.6 application
- Non-root user execution (`nonrtric`)
- Port 9090 exposed
- Configuration file mounting

**Build Process:**
1. **Maven Build Required:** The Dockerfile expects a JAR file in `target/` directory
2. **Java 17 Required:** Project uses Spring Boot 3.0.6 which requires Java 17
3. **Maven Repository Issue:** Initial build failed due to corrupted POM files in local Maven repository
4. **Solution Applied:** Cleaned Maven repository and rebuilt with Java 17

**Fixes Applied:**
- Installed Java 17: `sudo apt install -y openjdk-17-jdk`
- Set Java 17 as default: `export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`
- Cleaned Maven repository: `rm -rf ~/.m2/repository`
- Built Maven project: `mvn clean package -DskipTests`
- Built Docker image with JAR argument: `--build-arg JAR=nonrtric-gateway-1.3.0-SNAPSHOT.jar`

**Build Command:**
```bash
docker build --network=host -t portal-nonrtric-gateway:test --build-arg JAR=nonrtric-gateway-1.3.0-SNAPSHOT.jar -f Dockerfile .
```

**Warnings:**
- `FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 20)` - Minor casing inconsistency

#### 3.2.2 `./webapp-frontend/Dockerfile` ✅ SUCCESS

**Purpose:** Angular frontend application for O-RAN Non-RT RIC Control Panel

**Base Image:** 
- Multi-stage build using `node:14-alpine` for build stage
- Final stage: `nginx:alpine`

**Key Features:**
- Angular 9 application
- Multi-stage build for optimized production image
- Nginx web server
- Unit testing with Karma and Chrome Headless
- Production build optimization

**Build Process:**
1. **Stage 1 (Build):** Node.js 14 Alpine for building Angular application
2. **Dependencies:** `npm install` for package installation
3. **Testing:** Unit tests with Chrome Headless browser
4. **Build:** Production build with `npm run-script build:prod`
5. **Stage 2 (Runtime):** Nginx Alpine for serving static files

**Build Command:**
```bash
docker build --network=host -t portal-nonrtric-frontend:test -f Dockerfile .
```

**Warnings:**
- `LegacyKeyValueFormat: "ENV key=value" should be used instead of legacy "ENV key value" format (line 28)` - Minor ENV format suggestion
