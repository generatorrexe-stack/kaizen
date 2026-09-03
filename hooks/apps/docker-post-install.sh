#!/bin/bash
# Adds the user who started Kaizen to docker after a successful installation.
set -euo pipefail
exec pkexec --disable-internal-agent --action-id io.github.kaizen.package.configure \
  /usr/lib/kaizen/kaizen-privileged docker-add-invoker-to-group
