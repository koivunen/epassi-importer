
#!/usr/bin/env bash
set -Eeuo pipefail

export TZ=Europe/Helsinki

cd /opt/epassi
exec /usr/bin/flock -n /opt/epassi/.run_main.lock \
  /opt/epassi/.venv/bin/python /opt/epassi/main.py \
  >>/opt/epassi/run_main.log 2>&1

