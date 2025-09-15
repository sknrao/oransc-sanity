### Dockerfiles build verification (macOS)

Scope
- Verified all Dockerfiles under `solution/**` build on macOS using Docker Buildx targeting linux/amd64.

Discovered Dockerfiles
- `solution/smo/oam/pm/pm-rapp/Dockerfile`
- `solution/smo/apps/flows/Dockerfile`
- `solution/infra/dhcp-tester/Dockerfile`
- `solution/smo/oam/ves-collector/Dockerfile`

Build commands used
```bash
docker buildx build --platform linux/amd64 --load \
  /Users/jitmisra/Desktop/oam/solution/smo/oam/pm/pm-rapp -t oam/pm-rapp:local

docker buildx build --platform linux/amd64 --load \
  /Users/jitmisra/Desktop/oam/solution/smo/apps/flows -t oam/flows:local

docker buildx build --platform linux/amd64 --load \
  /Users/jitmisra/Desktop/oam/solution/infra/dhcp-tester -t oam/dhcp-tester:local

docker buildx build --platform linux/amd64 --load \
  /Users/jitmisra/Desktop/oam/solution/smo/oam/ves-collector -t oam/ves-collector:local
```

Build results (successful)
- `oam/pm-rapp:local` — ~37 MB
- `oam/flows:local` — ~605 MB
- `oam/dhcp-tester:local` — ~189 MB
- `oam/ves-collector:local` — ~373 MB