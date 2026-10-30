#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import requests
import yaml

PROMETHEUS_YML_PATH = os.environ.get("PROMETHEUS_YML_PATH", "/etc/prometheus/prometheus.yml")
GRAFANA_PROM_URL = os.environ.get("GRAFANA_PROM_URL", "").rstrip("/")
GRAFANA_INSTANCE_ID = os.environ.get("GRAFANA_INSTANCE_ID", "")
GRAFANA_API_TOKEN = os.environ.get("GRAFANA_API_TOKEN", "")
OUTPUT_FILE = "network_data.json"


def load_blackbox_targets(path):
    with open(path) as f:
        config = yaml.safe_load(f)
    for job in config.get("scrape_configs", []):
        if job.get("job_name") == "blackbox_network":
            targets = []
            for sc in job.get("static_configs", []):
                targets.extend(str(t) for t in sc.get("targets", []))
            return targets
    return []


def query_probe_status():
    if not (GRAFANA_PROM_URL and GRAFANA_INSTANCE_ID and GRAFANA_API_TOKEN):
        print("[warn] Missing Grafana Cloud credentials: device status will be 'unknown'.")
        return {}
    try:
        r = requests.get(
            f"{GRAFANA_PROM_URL}/api/v1/query",
            params={"query": 'probe_success{job="blackbox_network"}'},
            auth=(GRAFANA_INSTANCE_ID, GRAFANA_API_TOKEN),
            timeout=30,
        )
        r.raise_for_status()
        results = r.json()["data"]["result"]
    except Exception as e:
        print(f"[warn] Could not query Grafana Cloud: {e}")
        return {}
    return {
        item["metric"].get("instance", "?"): "up" if item["value"][1] == "1" else "down"
        for item in results
    }


def collect_tailscale():
    try:
        out = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True, text=True, check=True, timeout=30,
        ).stdout
        status = json.loads(out)
    except Exception as e:
        print(f"[warn] Could not read Tailscale status: {e}")
        return []

    nodes = []
    for node in [status.get("Self", {}), *status.get("Peer", {}).values()]:
        if not node:
            continue
        ips = node.get("TailscaleIPs") or []
        nodes.append({
            "name": node.get("HostName", "unknown"),
            "tailscale_ip": ips[0] if ips else "unknown",
            "os": node.get("OS", "unknown"),
            "online": node.get("Online", False),
        })
    return nodes


def main():
    try:
        targets = load_blackbox_targets(PROMETHEUS_YML_PATH)
    except Exception as e:
        sys.exit(f"[error] Could not read {PROMETHEUS_YML_PATH}: {e}")

    status_by_target = query_probe_status()
    data = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "local_devices": [
            {"target": t, "status": status_by_target.get(t, "unknown")} for t in targets
        ],
        "tailscale_nodes": collect_tailscale(),
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Data saved to {OUTPUT_FILE}")
    print(f"  Devices: {len(data['local_devices'])}")
    print(f"  Tailscale nodes: {len(data['tailscale_nodes'])}")


if __name__ == "__main__":
    main()