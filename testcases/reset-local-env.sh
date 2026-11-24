#!/bin/bash
# Agentic TestOps — reset the LOCAL TrustBase test environment between runs.
#  1. Re-applies the database fixtures (testcases/trustbase-fixtures.sql).
#  2. Clears rate-limit counters (keys `rl:*`) in the local Redis so earlier runs do not
#     consume the hourly budgets (sign-up 5/h/IP, order creation 20/h/IP) of the next run.
# Only touches the local Docker containers `trustbase-postgres` and `trustbase-redis`.
set -euo pipefail
export MSYS_NO_PATHCONV=1
DIR="$(cd "$(dirname "$0")" && pwd)"

wsl -e docker exec -i trustbase-postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At -F" | " -v ON_ERROR_STOP=1 -f -' < "$DIR/trustbase-fixtures.sql" | tail -8

wsl -e docker exec trustbase-redis sh -c 'n=0; for k in $(redis-cli --scan --pattern "rl:*"); do redis-cli del "$k" >/dev/null; n=$((n+1)); done; echo "rate-limit keys cleared: $n"'
