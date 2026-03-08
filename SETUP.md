# Pre-Lab Setup Guide

**EEE5138Z — Broadband Communication Networks**  
**Department of Electrical Engineering · University of Cape Town**

Complete **all sections** and tick off every item in the [verification checklist](#8-verification-checklist) before arriving on Day 1 (Monday, 9 March 2026).

---

## Contents

1. [General Information](#1-general-information)
2. [Base System](#2-base-system)
3. [Repository Cloning](#3-repository-cloning)
4. [Lab 1 — Docker](#4-lab-1--docker)
5. [Lab 2 — Mininet & POX](#5-lab-1--mininet--pox)
6. [Lab 3 — OpenAirInterface on SLICES-RI](#6-lab-2--openairinterface-oai-on-slices-ri)
7. [Lab 4 — Edge AI Blueprint](#7-lab-3--edge-ai-blueprint)
8. [Verification Checklist](#8-verification-checklist)
9. [Troubleshooting](#9-troubleshooting)
10. [Still Stuck?](#10-still-stuck)

---

## 1. General Information

This course is offered by the Department of Electrical Engineering at the University of Cape Town. It will be presented as a block course running from **9–13 March 2026**. All laboratory sessions will be conducted in the **BTF Lab, 4th Floor, Menzies Building**.

### Lab schedule

| Lab | Day | Title | Core Stack |
|-----|-----|-------|------------|
| Lab 1 | Mon 9 Mar | Introduction to Containers | Docker, Docker Compose |
| Lab 2 | Tue 10 Mar | SDN with Mininet | Mininet, POX, OpenFlow |
| Lab 3 | Wed 11 Mar | Deploying a 5G SA Network | OpenAirInterface, SLICES-RI |
| Lab 4 | Thu 12 Mar | Edge AI Blueprint Deployment | Ansible, Docker, JupyterLab, Prometheus, DIGITAfrica |

> **Note:** There is no laboratory session on Day 5 (Fri 13 Mar). That session will be used for project topic proposals and a 6G lecture.

### Assessment

Lab reports contribute to the **Assignments & Labs** component (10% of the final mark). Reports must be submitted via the course submission portal by **Friday 13 March 2026 at 17:00**.

---

## 2. Base System

All labs for this course are tested on **Ubuntu 22.04 LTS only**. Ensure your environment matches one of the supported configurations below before proceeding.

| Acceptable Environment | Notes |
|------------------------|-------|
| Native Ubuntu 22.04 LTS | Preferred |
| VirtualBox / VMware VM running Ubuntu 22.04 LTS | Allocate at least 16 GB RAM to the VM |
| WSL2 with Ubuntu 22.04 LTS | Labs 0–1 only — TUN/TAP interfaces are not supported for Labs 2–3 |

> **Note:** No SDR hardware is required — all radio simulation is software-based.

### 2.1 Environment setup

If you do not have a supported environment, set one up using one of the following methods:

1. **Choose and install Ubuntu 22.04 LTS** using your preferred method:
   - **Native:** Download the ISO from https://ubuntu.com/download/alternative-downloads and follow the guide at https://ubuntu.com/tutorials/install-ubuntu-desktop
   - **Virtual Machine:** Download the ISO, then install [VirtualBox](https://www.virtualbox.org) or [VMware](https://knowledge.broadcom.com/external/article/344595/downloading-and-installing-vmware-workst.html) and follow the setup guide at https://ubuntu.com/tutorials/how-to-run-ubuntu-desktop-on-a-virtual-machine-using-virtualbox
     > **Note:** Allocate at least 16 GB RAM when creating your VM.
   - **WSL2 (Windows only):** Search for *Ubuntu 22.04 LTS* in the Microsoft Store, click Install, and follow the guide at https://ubuntu.com/tutorials/install-ubuntu-on-wsl2-on-windows-11-with-gui-support

2. **Verify your setup** — open a terminal and run:

```bash
lsb_release -a
```

Confirm `Ubuntu 22.04 LTS` appears in the output before proceeding.

### 2.2 Update and install common tools

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
  curl wget git build-essential net-tools \
  python3 python3-pip python3-venv \
  software-properties-common tmux \
  tshark wireshark iperf3 tcpdump \
  iproute2 iputils-ping
```

**Verify:**

```bash
dpkg -l curl wget git build-essential net-tools \
  python3 python3-pip python3-venv \
  software-properties-common tmux \
  tshark wireshark iperf3 tcpdump \
  iproute2 iputils-ping
```

If everything is installed, each package will show a line starting with `ii`.

### 2.3 Add yourself to the wireshark group

```bash
sudo usermod -aG wireshark $USER && newgrp wireshark
```

**Verify:**

```bash
id -nG $USER | grep wireshark
```

Expected output: `wireshark`

---

## 3. Repository Cloning

After setting up your environment, clone the course repository to your local machine. It contains all required lab materials and configuration files.

```bash
git clone https://github.com/joycebm/eee5138z-labs.git
cd eee5138z-labs
```

---

## 4. Lab 1 — Docker

```bash
# Remove old Docker installs
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null

# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine + Compose plugin
sudo apt update
sudo apt install -y \
  docker-ce docker-ce-cli containerd.io \
  docker-buildx-plugin docker-compose-plugin

# Run without sudo
sudo usermod -aG docker $USER && newgrp docker
```

### 4.1 Verify

```bash
docker run hello-world       # must print "Hello from Docker!"
docker compose version       # must show v2.x.x or v5.x.x
```

---

## 5. Lab 2 — Mininet & POX

### 5.1 Mininet

```bash
git clone https://github.com/mininet/mininet
cd mininet
sudo util/install.sh -a      # ~15 min; installs OVS, Wireshark dissectors
cd ~
```

#### 5.1.1 Verify

```bash
sudo mn -c && sudo mn --test pingall
# Expected: Results: 0% dropped (2/2 received)
```

### 5.2 POX SDN controller
Only install in pox was not installed by the mininet command. 
```bash
git clone https://github.com/noxrepo/pox.git ~/pox
```

**Verify:**

```bash
python3 ~/pox/pox.py --version
# Expected: prints POX version string
```

> **Note:** POX runs directly from the cloned directory — no pip install needed.

---

## 6. Lab 3 — OpenAirInterface (OAI) on SLICES-RI

Lab 3 deploys OAI on a **SLICES-RI cloud VM** — your laptop only needs the SLICES CLI, an SSH key, and an account. The OAI Docker images run entirely inside the remote VM.

### 6.1 Create a SLICES-RI account

Visit the registration page and follow the instructions **before the course**:

> https://doc.slices-ri.eu/SupportingServices/getanaccount.html

Then join the tutorial project using this link:

> https://portal.slices-ri.eu/invite/post5g-beta?key=OL9PXXTnYKEvCuUS

### 6.2 Install the SLICES CLI

```bash
# Create and activate a Python virtual environment
python3 -m venv ~/slices-venv
source ~/slices-venv/bin/activate

# Install CLI and results publishing tool
pip install slices-cli --extra-index-url=https://doc.slices-ri.eu/pypi/
pip install git+https://gitlab.inria.fr/slices-ri/publish_results.git
```

> Add `source ~/slices-venv/bin/activate` to your `~/.bashrc` so the CLI is available each session.

### 6.3 Authenticate the CLI

```bash
slices auth login
```

Follow the URL in the output to authorise the CLI via the SLICES portal.

### 6.4 Ensure you have an SSH key pair

```bash
ls ~/.ssh/id_ed25519.pub
```

If the file does not exist, generate a key:

```bash
ssh-keygen -t ed25519
```

### 6.5 Check AVX2 (for students using a BTF Lab PC as fallback)

If you plan to run OAI locally as a fallback, verify AVX2 support:

```bash
lscpu | grep avx2
```

> **Note:** If your laptop fails this check, use a BTF Lab PC — all lab machines support AVX2.

### 6.6 Pre-clone the LatinCom repo on your laptop (optional)

Not required — you will clone this inside the SLICES VM on lab day. But if you want to browse the config files in advance:

```bash
git clone https://gitlab.inria.fr/slices-ri/latincom-2025.git ~/latincom-2025
```

---

## 7. Lab 4 — Edge AI Blueprint

Lab 4 uses **Ansible** to deploy Docker containers locally. No compilation is needed.

### 7.1 Install Ansible

```bash
sudo apt install -y ansible
pip3 install ansible
```

**Verify:**

```bash
ansible --version
# Expected: ansible [core 2.x.x] or higher
```

### 7.2 Install the community.docker Ansible collection

```bash
ansible-galaxy collection install community.docker
```

### 7.3 Verify Docker is running

```bash
docker info
# Expected: Server information without errors
```

> The blueprint playbook deploys containers to localhost — no remote SSH needed for this lab.

---

## 8. Verification Checklist

Tick off every item before **Monday 9 March**.

### 8.1 All labs

| Task | Done? |
|------|-------|
| Ubuntu 22.04 confirmed: `lsb_release -a` | ☐ |
| System updated: `sudo apt update && sudo apt upgrade -y` | ☐ |

### 8.2 Lab 1

| Task | Done? |
|------|-------|
| `docker run hello-world` succeeds | ☐ |
| `docker compose version` shows v2.x.x | ☐ |

### 8.3 Lab 2

| Task | Done? |
|------|-------|
| `sudo mn --test pingall` → 0% dropped | ☐ |
| `python3 ~/pox/pox.py --version` succeeds | ☐ |

### 8.4 Lab 3

| Task | Done? |
|------|-------|
| SLICES-RI account created and activated | ☐ |
| `post5g-beta` project joined via invite link | ☐ |
| `slices-venv` virtual environment created | ☐ |
| `slices auth login` completed successfully | ☐ |
| SSH key pair exists: `ls ~/.ssh/id_ed25519.pub` | ☐ |

### 8.5 Lab 4

| Task | Done? |
|------|-------|
| `ansible --version` returns 2.x+ | ☐ |
| `ansible-galaxy collection list \| grep community.docker` shows the collection | ☐ |
| `docker info` succeeds without errors | ☐ |

---

## 9. Troubleshooting

### 9.1 Docker: permission denied

```bash
sudo usermod -aG docker $USER && newgrp docker
```

### 9.2 Mininet: interface already exists

```bash
sudo mn -c
```

### 9.3 POX: command not found

If `pox.py` is not found:

```bash
ls ~/pox/pox.py
# If missing, re-clone:
git clone https://github.com/noxrepo/pox.git ~/pox
```

POX requires Python 3. If you see errors about Python 2 syntax:

```bash
python3 ~/pox/pox.py --version
```

Always invoke POX with `python3` explicitly if `./pox.py` fails.

### 9.4 Ansible: community.docker not found

```bash
ansible-galaxy collection install community.docker --force
```

### 9.5 OAI containers crash immediately (avx2 error)

```
Illegal instruction (core dumped)
```

Your CPU does not support AVX2. Use a BTF Lab PC.

---

## 10. Still Stuck?

Email **joyce.mwangama@uct.ac.za**. Include the output of:

```bash
lsb_release -a
lscpu | grep -E "Model|avx2"
```

...and the exact error message.
