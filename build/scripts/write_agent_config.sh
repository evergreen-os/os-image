#!/usr/bin/env bash
set -euo pipefail

enrollment_payload="/var/lib/evergreen/enrollment.json"
config_dir="/etc/evergreen/agent"
config_file="${config_dir}/agent.yaml"

mkdir -p "${config_dir}"

if [[ -s "${enrollment_payload}" ]]; then
  backend_url=$(jq -r '.backend_url // empty' "${enrollment_payload}" 2>/dev/null || true)
  tenant=$(jq -r '.tenant // empty' "${enrollment_payload}" 2>/dev/null || true)
else
  backend_url=""
  tenant=""
fi

cat <<CONFIG >"${config_file}"
apiVersion: evergreenos/v1
backend:
  url: "${backend_url}"
  tenant: "${tenant}"
updates:
  channel: "stable"
telemetry:
  enabled: true
CONFIG

touch /var/lib/evergreen/enrollment.complete
