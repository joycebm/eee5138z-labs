# Lab 4 — Edge AI Blueprint Deployment

**Day 4 · Thursday 12 March 2026 · 14:00–17:00**

> **Attribution** — This lab is based on the  
> [DIGITAfrica Edge AI Blueprint](https://gitlab.inria.fr/digitafrica/blueprints/services/edge-ai-blueprint)  
> from the DIGITAfrica Horizon Europe project (grant agreement No. 101133297),  
> licensed under CC BY 4.0.

---

## Overview

In previous labs you deployed network infrastructure (SDN switches, 5G core). In this lab you deploy **AI inference infrastructure at the network edge** — a Jupyter-based ML environment running as Docker containers on a single node, with resource monitoring via cAdvisor and node-exporter. This is the **Tier-0** deployment of the DIGITAfrica Edge AI Blueprint, designed for resource-constrained African research institutions.

You will provision the stack using **Ansible**, run two ML notebooks that demonstrate edge AI concepts relevant to African contexts (precision agriculture, training vs. inference cost), and use the monitoring endpoints to observe resource usage during inference.

**Duration:** 3 hours  
**Terminals needed:** 2–3

## Learning objectives

- Understand the DIGITAfrica Edge AI Blueprint architecture (Tier-0 / Tier-1)
- Deploy JupyterLab as a Docker container using an Ansible playbook
- Deploy a monitoring stack (cAdvisor + node-exporter) alongside the AI workload
- Run and interpret ML notebooks in a resource-constrained edge context
- Observe CPU/memory cost of training vs. inference using live metrics
- Discuss the design choices relevant to African connectivity and compute contexts

## Prerequisites

- [ ] Docker installed and running: `docker info` succeeds
- [ ] Ansible installed: `ansible --version` returns 2.x+
- [ ] `community.docker` collection installed: `ansible-galaxy collection list | grep community.docker`
- [ ] Course repo cloned with `lab4-edge-ai/` present

---

## Architecture

The **Tier-0** deployment runs entirely on a single node (your BTF Lab PC):

```
  ┌─────────────────────────────────────────────────────────────────┐
  │  BTF Lab PC  (Tier-0 Edge Node)                                 │
  │                                                                 │
  │  ┌─────────────────────────────┐   ┌────────────────────────┐  │
  │  │  digitafrica-tier0-jupyter  │   │  Monitoring stack      │  │
  │  │  jupyter/minimal-notebook   │   │  node-exporter :9100   │  │
  │  │  port 8888                  │   │  cadvisor      :8080   │  │
  │  │  /opt/digitafrica/notebooks │   └────────────────────────┘  │
  │  └─────────────────────────────┘                               │
  │                                                                 │
  │  Managed by: Ansible (localhost inventory)                      │
  └─────────────────────────────────────────────────────────────────┘
```

The blueprint also defines **Tier-1** (multi-node K3s cluster with JupyterHub and MLflow), but in this lab we focus on the simpler Tier-0 Docker deployment — the entry point designed for institutions with limited infrastructure.

> See [BLUEPRINT.md](./BLUEPRINT.md) for the full upstream blueprint documentation.

---

## Part 1 — Explore the blueprint repository

```bash
cd ~/eee5138z-labs/lab4-edge-ai
ls
```

Key files to review before deploying:

| File | Purpose |
|------|---------|
| `ansible.cfg` | Ansible configuration (SSH settings, inventory path) |
| `inventories/prod/hosts.ini` | Target node definitions (Tier-0 / Tier-1) |
| `inventories/prod/group_vars/all.yml` | Default variables (ports, passwords, paths) |
| `playbooks/site.yml` | Master playbook — selects roles based on host group |
| `roles/tier0_notebook_docker/` | Docker-based Jupyter deployment role |
| `roles/monitoring/` | cAdvisor + node-exporter deployment role |
| `notebooks/` | The two ML notebooks used in this lab |

Open `inventories/prod/group_vars/all.yml`:

```bash
cat inventories/prod/group_vars/all.yml
```

> **Question 1:** What port does the JupyterLab container expose? What is the default password, and where is it stored as a hash? What monitoring ports are used by node-exporter and cAdvisor?

---

## Part 2 — Configure for local deployment

The blueprint is designed for multi-node deployment over SSH. For this lab we run it **locally** (localhost). Edit the inventory to target your own machine:

```bash
cp inventories/prod/hosts.ini inventories/prod/hosts.ini.bak
```

Replace the contents of `inventories/prod/hosts.ini` with:

```ini
[tier0]
localhost ansible_connection=local
```

Install the required Ansible collections:

```bash
ansible-galaxy collection install -r requirements.yml
```

> **Question 2:** Open `requirements.yml`. Which Ansible collections are required and what do they provide? Why is `community.docker` needed rather than running `docker run` commands directly in shell tasks?

---

## Part 3 — Deploy the Tier-0 stack

### 3.1 Run the Ansible playbook

```bash
ansible-playbook -i inventories/prod/hosts.ini playbooks/site.yml
```

Watch the task output. Ansible will:

1. Run the `common` role (system dependencies, timezone)
2. Run the `docker` role (ensure Docker is installed and running)
3. Run the `tier0_notebook_docker` role (start JupyterLab container)
4. Run the `monitoring` role (start cAdvisor and node-exporter)

A successful run ends with a `PLAY RECAP` showing `failed=0`.

### 3.2 Verify the containers are running

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
```

Expected output:

```
NAMES                        IMAGE                                    STATUS    PORTS
digitafrica-tier0-jupyter    jupyter/minimal-notebook:python-3.11    Up ...    0.0.0.0:8888->8888/tcp
cadvisor                     gcr.io/cadvisor/cadvisor:latest          Up ...    0.0.0.0:8080->8080/tcp
node-exporter                prom/node-exporter:latest                Up ...    (host network)
```

### 3.3 Access JupyterLab

Open a browser and navigate to:

```
http://localhost:8888
```

Enter the password: **`digitafrica`**

You should see the JupyterLab interface with a `digitafrica/` folder containing two notebooks.

> **Question 3:** How does the Ansible task pass the password to the Jupyter container? Look at `roles/tier0_notebook_docker/tasks/install.yml`. What format is the password stored in (`tier0_notebook_password_hash`)? Why is a hash used rather than a plaintext password?

---

## Part 4 — Run the Precision Agriculture notebook

Open the notebook:

```
digitafrica/ → 01_precision_agriculture_edge_ml.ipynb
```

This notebook demonstrates a **regression model for crop yield prediction** using synthetic sensor data (soil moisture, temperature, rainfall) — a use case directly relevant to African smallholder farming contexts.

Run all cells (`Shift-Enter` or Kernel → Run All Cells) and observe:

- The scatter plot of soil moisture vs. yield
- The model coefficients (feature influence plot)
- The prediction for a sample sensor reading

> **Question 4:** What does the model predict for soil_moisture=35, temperature=28, rainfall=3? Which input feature has the largest positive influence on yield? What are the limitations of training and running this model on an edge device with limited RAM?

---

## Part 5 — Run the Training vs. Inference notebook

Open:

```
digitafrica/ → 02_ml_basics_training_vs_inference.ipynb
```

This notebook measures and compares the **compute cost of training vs. inference** on edge hardware — a core concern when deploying AI on resource-constrained nodes.

Run all cells and observe:

- Training time vs. inference time (bar chart)
- How accuracy changes with training iterations

While the notebook is running, switch to a second terminal and observe live container resource usage from cAdvisor:

```
http://localhost:8080/containers/
```

Navigate to the `digitafrica-tier0-jupyter` container to see CPU and memory usage in real time.

> **Question 5:** What is the ratio of training time to inference time in your results? What does this imply for how an edge AI deployment should be structured (i.e., where should training happen vs. where should inference happen)? How does this relate to the DIGITAfrica blueprint's separation of Tier-0 (edge) and Tier-1 (server) roles?

---

## Part 6 — Inspect node-level metrics

Node-exporter exposes raw system metrics in Prometheus format. Query them directly:

```bash
curl -s http://localhost:9100/metrics | grep -E "^node_cpu_seconds|^node_memory_MemAvailable"
```

> **Question 6:** What percentage of your available RAM is used after deploying the full stack? Look at `node_memory_MemTotal_bytes` and `node_memory_MemAvailable_bytes`. Is this deployment feasible on a Raspberry Pi 5 (the reference hardware in the blueprint README)?

---

## Part 7 — Teardown

When you are finished, stop and remove all containers:

```bash
ansible-playbook -i inventories/prod/hosts.ini playbooks/site.yml \
  -e digitafrica_uninstall=true
```

Verify:

```bash
docker ps -a | grep -E "jupyter|cadvisor|node-exporter"
# should return nothing
```

---

## Part 8 — Reflection: Tier-0 vs Tier-1

The blueprint README describes a Tier-1 deployment that adds:

- A multi-node **K3s** Kubernetes cluster
- **JupyterHub** (multi-user, with OIDC authentication via Keycloak)
- **MLflow** (experiment tracking and model registry)
- **Prometheus + Grafana** (full monitoring stack)

> **Question 7 (Discussion):** In the context of a university research lab in sub-Saharan Africa with intermittent internet connectivity and a small number of edge nodes, what factors would determine whether to use Tier-0 or Tier-1? Consider: number of users, need for model versioning, network reliability, and hardware availability.

---

## Submission

Write a lab report containing:

- Answers to Questions 1–7
- Screenshot of the JupyterLab interface showing both notebooks
- Screenshot of the cAdvisor container stats page during notebook execution
- Screenshot of the feature influence plot from Notebook 1

Submit via the course portal by **Friday 13 March 2026 at 17:00**.

---

## Navigation

← [Lab 3 — 5G SA Network](../lab3-5g-oai/README.md)
