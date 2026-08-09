#!/bin/bash
set -e

mkdir -p /run/sshd /root/.ssh
chmod 700 /root/.ssh

ssh-keygen -A >/dev/null 2>&1 || true

# Allow key-based root login for this isolated lab.
sed -i 's/^#\?PermitRootLogin .*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sed -i 's/^#\?PubkeyAuthentication .*/PubkeyAuthentication yes/' /etc/ssh/sshd_config
sed -i 's/^#\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config

exec /usr/sbin/sshd -D -e
