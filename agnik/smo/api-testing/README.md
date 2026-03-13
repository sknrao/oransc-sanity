# O-RAN Bruno API Collection

This folder contains a [Bruno](https://www.usebruno.com/) API collection for testing O-RAN components (SMO and RIC).

## Collection Structure

| Folder | Service | Description |
|--------|---------|-------------|
| `a1pms` | Non-RT RIC A1PMS | Policy management service (A1-P). |
| `influxdb` | InfluxDB | Metrics and performance data storage. |
| `keycloak` | Keycloak | Identity and access management. |
| `sdnc` | SDNC / SDNR | NETCONF topology and O1 interface. |
| `controlpanel` | Control Panel | SMO Dashboard interface. |

## How to Use

1.  **Download Bruno**: Install the Bruno client on your local machine.
2.  **Import Collection**: Click "Open Collection" in Bruno and select this folder.
3.  **Run Tests**: You can run individual requests or the entire collection to verify system health.

## Configuration (Current Cluster)
The collection is pre-configured for the `hpe15`/`hpe16` cluster:
- **Host**: `hpe15.anuket.iol.unh.edu`
- **InfluxDB Port**: `32717`
- **SDNR Port**: `30267`
- **Keycloak Port**: `32661`
- **MinIO UI Port**: `30215`
