# Lab 3 — Deploying a 5G SA Network with OpenAirInterface

**Day 3 · Wednesday 11 March 2026 · 14:00–17:00**

> **Attribution** — This lab replicates the  
> [SLICES-RI LatinCom 2025 tutorial](https://gitlab.inria.fr/slices-ri/latincom-2025)  
> by Damien Saucez (Inria), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

## Overview

You will deploy a complete **5G Standalone (SA)** network in software using **OpenAirInterface (OAI)** and Docker Compose on a **SLICES-RI virtual machine**. The stack includes the full 5G Core (AMF, SMF, UPF, AUSF, UDM, UDR, NRF), a simulated gNB via OAI RFSim, and two virtual UEs — no radio hardware required.

You will capture the control-plane signalling between all 5G functions using tshark, analyse the NAS/NGAP registration procedure, measure end-to-end throughput with iperf3, and publish your results to the SLICES Measurement Repository Service.

**Duration:** 3 hours  
**Terminals needed:** 5 (use `tmux` — see quick reference below)

## Learning objectives

- Access a research infrastructure (SLICES-RI) and provision a cloud VM via CLI
- Deploy and start all OAI 5G core network functions in Docker
- Understand the role of each 3GPP network function (AMF, SMF, UPF, NRF, …)
- Attach a simulated gNB and two virtual UEs
- Capture and analyse 5GC control-plane traffic (NGAP, NAS, SBI, PFCP)
- Verify end-to-end data-plane connectivity and measure throughput
- Publish experimental results to an open data repository

## Prerequisites

- [ ] Laptop with Ubuntu 22.04 (or WSL2 Ubuntu 22.04)
- [ ] Python 3 and `python3-venv` installed
- [ ] SSH key pair available (`~/.ssh/id_ed25519`)
- [ ] SLICES-RI account registered (see Section 1 below)

> **Note:** The 5G functions run in the SLICES cloud VM — your laptop only needs the SLICES CLI and an SSH client.

---

## tmux quick reference

```
tmux new -s lab3        start a session
Ctrl-b "               split pane horizontally
Ctrl-b %               split pane vertically
Ctrl-b ← → ↑ ↓        move between panes
Ctrl-b z               zoom/unzoom current pane
Ctrl-b c               new window
Ctrl-b 0–9             switch window
```

Suggested layout: window 0 with 3 panes (core · tshark · watch), window 1 with 2 panes (gNB · UE logs).

---

## Architecture

```
              ┌──────────────────────────── Docker network: oaiworkshop ──────────────────────────┐
              │                                                                                    │
              │  mysql   NRF   AUSF   UDM   UDR   AMF   SMF   UPF   ext-dn                       │
              │   └──────────────────────────┬─────────────────────────────┘                      │
              │                              │ N2 (NGAP/SCTP :38412)                              │
              │                           oai-gnb (RFSim)                                         │
              │                        oai-nr-ue   oai-nr-ue2                                     │
              └────────────────────────────────────────────────────────────────────────────────────┘

Interfaces captured by tshark on oaiworkshop:
  SBI (HTTP/2 :80/:8080)  — NF-to-NF service-based interface
  PFCP (:8805)            — SMF–UPF session management
  SCTP (:38412)           — gNB–AMF N2 / NGAP
  ICMP                    — UE data-plane ping tests
```

---

## Part 1 — Get access to SLICES-RI

SLICES-RI is an open European research infrastructure. You must register and activate an account before proceeding.

### 1.1 Create a SLICES-RI account

Visit the registration page and follow the instructions:

> https://doc.slices-ri.eu/SupportingServices/getanaccount.html

### 1.2 Join the tutorial project

After creating your account, join the `post5g-beta` project using this link:

> https://portal.slices-ri.eu/invite/post5g-beta?key=OL9PXXTnYKEvCuUS

This gives you access to all project services and the ability to create experiments.

---

## Part 2 — Prepare your experimental environment

All SLICES interactions happen via the **SLICES CLI**, a Python tool linked to your account. Install it inside a virtual environment to avoid affecting your system.

### 2.1 Install the SLICES CLI

On your **laptop**:

```bash
# Install venv dependencies if needed
sudo apt install -y python3 python3-pip python3-venv

# Create and activate virtual environment
python3 -m venv slices-venv
source slices-venv/bin/activate

# Install CLI and results publishing tool
pip install slices-cli --extra-index-url=https://doc.slices-ri.eu/pypi/
pip install git+https://gitlab.inria.fr/slices-ri/publish_results.git
```

> To exit the virtual environment later, use `deactivate`.

### 2.2 Authenticate the CLI

```bash
slices auth login
```

Follow the URL; it redirects to the SLICES portal where you authorise the CLI to access your account.

---

## Part 3 — Create a virtual machine in SLICES

SLICES organises resources into **projects** → **experiments** → **VMs**.

### 3.1 Select the project and create an experiment

```bash
slices project use post5g-beta

slices experiment create experiment-tutorial --duration 3h
```

> **Warning:** Experiment names must be unique within a project. Change the name if a conflict occurs.

### 3.2 Set environment variables

We use the Gent 1 VM site in Belgium (`be-gent1-bi-vm1`):

```bash
export SLICES_BI_SITE_ID=be-gent1-bi-vm1
export SLICES_EXPERIMENT=experiment-tutorial
```

### 3.3 Register your SSH public key

```bash
slices pubkey register ~/.ssh/id_ed25519.pub
```

> If you don't have an SSH key yet, generate one with `ssh-keygen`.

### 3.4 Create the VM

```bash
slices bi create vm1 --duration 3h --image "Ubuntu 24.04.1" --flavor medium
```

### 3.5 Wait for the VM to come up

```bash
slices bi list-resources
```

Wait until the status column shows `up`:

```
Resources in experiment ...
┏━━━━━━━┳━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ ...   ┃ Name ┃ Status ┃ Created At     ┃ Expires At     ┃ Private IPv4┃
┡━━━━━━━╇━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━┩
│ ...   │ vm1  │ up     │ 2026-03-11 ... │ 2026-03-11 ... │ 10.10.x.x   │
└───────┴──────┴────────┴────────────────┴────────────────┴─────────────┘
```

### 3.6 SSH into the VM

```bash
slices bi ssh vm1
```

> To copy files between your laptop and the VM, use `slices bi scp`.

---

## Part 4 — Install dependencies and clone the repository

You are now in a shell **on the VM**. All remaining steps in Parts 4–8 run on the VM unless stated otherwise.

```bash
git clone https://gitlab.inria.fr/slices-ri/latincom-2025.git
cd latincom-2025
./utils/install_dependencies.sh
```

This installs Docker, tshark, iperf3, IP forwarding configuration, and other required tools.

> **Question 1:** Open `cn/conf/config.yaml`. What PLMN (MCC/MNC) is configured? Open `cn/database/oai_db.sql` — what IMSI values are registered for the two UEs?

---

## Part 5 — Deploy the 5G Core Network

Navigate to the deployment directory:

```bash
cd ~/latincom-2025/cn
```

> Use `tmux` to manage multiple terminals within the VM.

### 5.1 Create the Docker network and start the database

Starting only MySQL creates the `oaiworkshop` Docker bridge network that tshark will capture on:

```bash
docker compose -f docker-compose.yml up -d mysql
```

### 5.2 Start tshark capture (Terminal 2)

Open a **second terminal** in the VM and start capturing:

```bash
sudo tshark -i oaiworkshop \
  -f "sctp or port 80 or port 8080 or port 8805 or icmp or port 3306" \
  -w - | sudo tee ~/latincom-2025/results/traffic.pcap >/dev/null
```

### 5.3 Start the full 5G Core (Terminal 1)

Return to Terminal 1 and start all core functions:

```bash
docker compose -f docker-compose.yml up -d
```

### 5.4 Monitor startup (Terminal 3)

Open a **third terminal** and watch the container health:

```bash
watch docker compose -f docker-compose.yml ps -a
```

Wait until all components show `Up (healthy)`:

```
mysql        Up (healthy)
oai-amf      Up (healthy)
oai-ausf     Up (healthy)
oai-ext-dn   Up (healthy)
oai-nrf      Up (healthy)
oai-smf      Up (healthy)
oai-udm      Up (healthy)
oai-udr      Up (healthy)
oai-upf      Up (healthy)
```

> **Question 2:** Look at `cn/docker-compose.yml`. What is the startup dependency order? Which NF registers with the NRF first, and why does that matter?

### 5.5 Follow AMF logs (Terminal 4)

```bash
docker logs oai-amf -f
```

### 5.6 Follow SMF logs (Terminal 5)

```bash
docker logs oai-smf -f
```

---

## Part 6 — Attach the gNB and UEs

All commands from Terminal 1 (in `~/latincom-2025/cn`).

### 6.1 Start the gNB

```bash
docker compose -f docker-compose-ran.yml up -d oai-gnb
```

Watch Terminal 3 until `oai-gnb` is `healthy`. In Terminal 4 (AMF logs) you should see:

```
|  Index |    Status   |  Global Id  |   gNB Name   |   PLMN   |
|    1   |  Connected  |   0xE000    | gnb-rfsim    |  001,01  |
```

### 6.2 Start UE 1

```bash
docker compose -f docker-compose-ran.yml up -d oai-nr-ue
```

Watch the AMF logs — a successful registration looks like:

```
|  Index |   5GMM State   |       IMSI       | ... |
|    1   | 5GMM-REGISTERED| 001010000000101  | ... |
```

Verify the UE tunnel interface has an IP address:

```bash
docker exec oai-nr-ue ip addr show dev oaitun_ue1
```

### 6.3 (Optional) Start UE 2

```bash
docker compose -f docker-compose-ran.yml up -d oai-nr-ue2
```

> **Question 3:** What IP address did UE 1 receive on `oaitun_ue1`? Which network function assigned it, and through which interface/protocol?

---

## Part 7 — Test data-plane connectivity and throughput

### 7.1 Ping tests from UE 1

```bash
docker exec -it oai-nr-ue bash
ping -I oaitun_ue1 8.8.8.8 -c 4        # towards the Internet
ping -I oaitun_ue1 10.0.0.1 -c 4        # towards the UPF N6 gateway
ping -I oaitun_ue1 192.168.70.135 -c 4  # towards oai-ext-dn (traffic server)
exit
```

### 7.2 iperf3 throughput test

Start the iperf3 server on the external data network container:

```bash
docker exec -it oai-ext-dn iperf3 -s
```

Install iperf3 inside the UE container (it is not included by default):

```bash
docker exec -it oai-nr-ue bash
apt update && apt install -y iperf3
```

Run uplink test (UE → ext-dn):

```bash
iperf3 -B <ue_ip> -c 192.168.70.135
```

Run downlink test (ext-dn → UE):

```bash
iperf3 -B <ue_ip> -c 192.168.70.135 -R
exit
```

> **Question 4:** Record your uplink and downlink throughput values. What limits the throughput in an RFSim environment?

---

## Part 8 — Analyse logs and PCAP

### 8.1 Stop tshark

In Terminal 2, press `Ctrl-C`.

### 8.2 Collect all container logs

```bash
for fct in oai-amf oai-ausf oai-ext-dn oai-nrf oai-smf oai-udm oai-udr oai-upf oai-gnb oai-nr-ue oai-nr-ue2
do
  docker logs $fct > ~/latincom-2025/results/$fct.stdout.log \
                   2> ~/latincom-2025/results/$fct.stderr.log
done
```

### 8.3 Copy results to your laptop

On your **laptop**:

```bash
mkdir -p results
slices bi scp -r vm1:latincom-2025/results/* results/
```

Open `results/traffic.pcap` in Wireshark. You should observe the following NGAP message sequence for each UE registration:

1. NGSetupRequest / NGSetupResponse
2. InitialUEMessage → Registration Request
3. DownlinkNASTransport → Identity Request / Response
4. Authentication Request / Response
5. Security Mode Command / Complete
6. Registration Complete
7. PDU Session Establishment Request / Accept
8. PDUSessionResourceSetupRequest / Response

For a full explanation of these procedures, see:  
https://www.sharetechnote.com/html/5G/5G_NGAP.html

> **Question 5:** Identify five distinct NGAP procedure types visible in your PCAP. For each, state the direction (UE→AMF or AMF→UE) and its purpose in the registration flow.

---

## Part 9 — Publish results to SLICES MRS

The **Measurement Repository Service (MRS)** is an open registry for experimental datasets. Publish your results so they can be cited in your report.

On your **laptop** (with the `slices-venv` virtual environment active):

```bash
export ID_TOKEN=$(slices auth id-token "https://mrs-portal.slices-staging.slices-be.eu")
export DMI_TOKEN=$(slices auth get-for-audience "https://mrs-portal.slices-staging.slices-be.eu")
publish-dataset --data-location results
```

Follow the on-screen prompts. Once complete, your dataset will appear on the MRS dashboard:  
https://mrs-portal.slices-staging.slices-be.eu

---

## Part 10 — Teardown

On the VM, ensure you are in `~/latincom-2025/cn` and run:

```bash
docker compose -f docker-compose-ran.yml down -t2 -v
docker compose -f docker-compose.yml down -t2 -v
```

---

## Submission

Write a lab report containing:

- Answers to Questions 1–5
- Your MRS dataset URL (from Part 9)
- Wireshark screenshot showing the NGAP Registration Request sequence

Submit via the course portal by **Friday 13 March 2026 at 17:00**.

---

## Navigation

← [Lab 2 — SDN with Mininet](../lab2-mininet/README.md) · [Lab 4 — Edge AI](../lab4-edge-ai/README.md) →
