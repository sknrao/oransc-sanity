### oam-tr069-adapter Dockerfiles build verification (linux/amd64)

Scope
- Built all Dockerfiles under `oam-tr069-adapter/**` for linux/amd64 using Docker Buildx.
- Built prerequisites (Maven JARs) in a containerized Maven environment.

Build steps
```bash
# 1) Build Java artifacts (skip tests; no docker plugin execution)
docker run --rm -u $(id -u):$(id -g) \
  -v $PWD:/workspace -w /workspace \
  -v $HOME/.m2:/var/maven/.m2 -e MAVEN_CONFIG=/var/maven/.m2 \
  maven:3.8.7-eclipse-temurin-8 \
  mvn -B -DskipTests -Ddocker.skip=true clean package

# 2) Build images
docker buildx build --platform linux/amd64 --load -t tr069adapter-mariadb:local oam-tr069-adapter/db
docker buildx build --platform linux/amd64 --load -t tr069adapter-ves-agent:local \
  --build-arg JAR=ves-agent-1.0.0-SNAPSHOT.jar oam-tr069-adapter/ves-agent
docker buildx build --platform linux/amd64 --load -t tr069adapter-netconfig-mapper:local \
  --build-arg JAR=mapper-1.0.0-SNAPSHOT.jar oam-tr069-adapter/mapper
docker buildx build --platform linux/amd64 --load -t tr069adapter-factory:local \
  --build-arg JAR=factory-1.0.0-SNAPSHOT.jar oam-tr069-adapter/factory
docker buildx build --platform linux/amd64 --load -t tr069adapter-acs-initialpnpdb:local \
  --build-arg JAR=config-data-1.0.0-SNAPSHOT.jar oam-tr069-adapter/config-data
docker buildx build --platform linux/amd64 --load -t tr069adapter-netconf-server:local \
  --build-arg JAR=netconf-server-1.0.0-SNAPSHOT.jar oam-tr069-adapter/netconf-server
docker buildx build --platform linux/amd64 --load -t tr069adapter-nginx:local oam-tr069-adapter/nginx
docker buildx build --platform linux/amd64 --load -t tr069adapter-acs:local \
  --build-arg JAR=application-booter-1.0.0-SNAPSHOT.jar oam-tr069-adapter/acs/application-booter
```

Discovered Dockerfiles
- `oam-tr069-adapter/db/Dockerfile`
- `oam-tr069-adapter/ves-agent/Dockerfile`
- `oam-tr069-adapter/mapper/Dockerfile`
- `oam-tr069-adapter/factory/Dockerfile`
- `oam-tr069-adapter/config-data/Dockerfile`
- `oam-tr069-adapter/netconf-server/Dockerfile`
- `oam-tr069-adapter/nginx/Dockerfile`
- `oam-tr069-adapter/acs/application-booter/Dockerfile`

Build results
- tr069adapter-mariadb:local — SUCCESS
- tr069adapter-ves-agent:local — SUCCESS
- tr069adapter-netconfig-mapper:local — SUCCESS
- tr069adapter-factory:local — SUCCESS
- tr069adapter-acs-initialpnpdb:local — SUCCESS
- tr069adapter-netconf-server:local — SUCCESS
- tr069adapter-nginx:local — SUCCESS
- tr069adapter-acs:local — SUCCESS
