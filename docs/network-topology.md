<!-- Generado automáticamente por generate_docs.py el 2026-10-27T18:49:17.835855+00:00 usando el modelo 'gemini-3.5-flash'. Revisar antes de confiar en este contenido: ver docs/VALIDATION.md -->

## Network Topology

The network consists of local LAN devices monitored for reachability alongside Tailscale nodes configured for remote access. The local network includes six monitored targets comprising specific IP addresses (192.168.0.1, 192.168.0.50, and 192.168.0.49) and hostnames (Redmi-Note-13.local, Mac.local, and ipad.local). The Tailscale overlay network contains two nodes: a Linux system named "delta" and an Android device named "Redmi Note 13". Together, these records provide visibility into both direct local connectivity and virtual private network endpoints.

## Diagram

```mermaid
graph TD
    subgraph "Local Network"
        L1["192.168.0.1"]
        L2["192.168.0.50"]
        L3["192.168.0.49"]
        L4["Redmi-Note-13.local"]
        L5["Mac.local"]
        L6["ipad.local"]
    end

    subgraph "Tailscale Network"
        T1["delta (100.105.145.13)"]
        T2["Redmi Note 13 (100.120.166.102)"]
    end
```

## Current Status

* Redmi Note 13 (Tailscale IP: 100.120.166.102): Offline