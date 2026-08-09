# Task 4 — Simple Ansible Basics Lab

This version keeps the lab intentionally simple.

## Architecture

```text
Your machine
    |
    +-- Docker
         |
         +-- ansible-control
         |      Ansible
         |
         +-- agent1
         |      Ubuntu + SSH
         |
         +-- agent2
                Ubuntu + SSH
```

The control container connects to both Ubuntu containers using an SSH key.

## Requirements

- Docker
- Docker Compose
- An SSH key pair

## 1. Create your SSH key

On your host machine:

```bash
ssh-keygen -t ed25519
```

You can press Enter to accept the default path.

If you already have a key, you can use it instead.

## 2. Put your key into the lab

Create the directory:

```bash
mkdir -p ssh
```

Copy your private and public key:

```bash
cp ~/.ssh/id_ed25519 ssh/
cp ~/.ssh/id_ed25519.pub ssh/
```

The resulting directory should contain:

```text
ssh/
├── id_ed25519
└── id_ed25519.pub
```

**Never commit the private key.** Add `ssh/` to `.gitignore`.

## Alternative: use ssh-agent

If you want to use your host SSH agent:

```bash
ssh-add ~/.ssh/id_ed25519
```

However, because Docker does not automatically expose the host SSH agent, the simplest assessment setup is to mount the key into the control container as described above.

## 3. Build and start

From the project root:

```bash
docker compose up -d --build
```

Check:

```bash
docker compose ps
```

## 4. Enter the control container

```bash
docker compose exec control bash
```

Inside:

```bash
cd /workspace
chmod 600 /root/.ssh/id_ed25519
```

## 5. Test SSH manually

```bash
ssh -i /root/.ssh/id_ed25519 root@agent1
```

Then:

```bash
exit
```

Test agent2:

```bash
ssh -i /root/.ssh/id_ed25519 root@agent2
```

If these work, Ansible should work.

## 6. Test Ansible

```bash
ansible all -m ping
```

Expected:

```text
agent1 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
agent2 | SUCCESS => {
    "changed": false,
    "ping": "pong"
}
```

## 7. Run the playbook

```bash
ansible-playbook basic_setup.yml
```

The playbook:

1. Gathers facts.
2. Prints hostname.
3. Prints OS family.
4. Prints IP address.
5. Prints uptime.
6. Installs `curl`.
7. Creates `/tmp/ansible_lab`.
8. Copies `README.txt`.
9. Checks the SSH daemon.

## 8. Run it a second time

```bash
ansible-playbook basic_setup.yml
```

The second execution should have fewer changes because Ansible is idempotent.

Look at:

```text
PLAY RECAP
```

The goal is to show that already-correct resources report `changed=0`.

## 9. Verify the results

From your host:

```bash
docker exec ansible-agent1 cat /tmp/ansible_lab/README.txt
docker exec ansible-agent2 cat /tmp/ansible_lab/README.txt
```

Check curl:

```bash
docker exec ansible-agent1 curl --version
docker exec ansible-agent2 curl --version
```

## What each file does

### `inventory.ini`

Defines the two target hosts and tells Ansible which SSH key to use.

### `basic_setup.yml`

Contains the actual automation tasks.

### `ansible.cfg`

Sets the inventory and disables SSH host-key prompts for this disposable lab.

### Docker files

Create the Ansible control machine and two Ubuntu SSH targets.

## Screenshots required

Capture:

1. `ansible all -m ping`
   - `screenshots/01-ansible-ping.png`

2. First playbook execution
   - `screenshots/02-playbook-first-run.png`

3. Second playbook execution showing reduced changes
   - `screenshots/03-playbook-second-run.png`

## Important security note

This lab uses a private SSH key mounted into the control container.

For a real project:

- Do not commit private keys.
- Use SSH agents or Ansible Vault.
- Use a non-root account.
- Use `become` when administrative privileges are required.
- Do not disable host-key checking in production.

This configuration is intentionally simplified for the bonus assessment lab.
