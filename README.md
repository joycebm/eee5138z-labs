# EEE5138Z — Broadband Communication Networks

**Department of Electrical Engineering · University of Cape Town**  
**Block course: 9–13 March 2026 · BTF Lab, 4th Floor, Menzies Building**

---

## Lab schedule

| Lab | Day | Title | Core stack |
|-----|-----|-------|------------|
| [Lab 1](./lab1-containers/) | Mon 9 Mar | Introduction to Containers | Docker, Docker Compose |
| [Lab 2](./lab2-mininet/) | Tue 10 Mar | SDN with Mininet | Mininet, POX, OpenFlow |
| [Lab 3](./lab3-5g-oai/) | Wed 11 Mar | Deploying a 5G SA Network | OpenAirInterface, SLICES-RI |
| [Lab 4](./lab4-edge-ai/) | Thu 12 Mar | Edge AI Blueprint Deployment | Ansible, Docker, JupyterLab, Prometheus, DIGITAfrica|

> Day 5 (Fri 13 Mar) — no lab: project topic proposals + 6G lecture.

---

## Getting started

```bash
git clone https://github.com/joycebm/eee5138z-labs.git
cd eee5138z-labs
```

> ⚠️ **Read [SETUP.md](./SETUP.md) and complete all pre-lab checks before Day 1.**

---

## System requirements

| | Minimum | Recommended |
|---|---|---|
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS (native install) |
| CPU | 8 cores + AVX2 | 12+ cores |
| RAM | 16 GB | 32 GB |
| Disk | 60 GB free | 80 GB free |

No SDR hardware is required — all radio simulation is software-based.

---

## Assessment

Lab reports contribute to the **Assignments & Labs** component (10% of final mark).  
Submission deadline: **Friday 13 March 2026, 17:00** via the course submission portal.

---

## Attribution

Lab 3 replicates the [SLICES-RI LatinCom 2025 tutorial](https://gitlab.inria.fr/slices-ri/latincom-2025)
by Damien Saucez (Inria), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Lab 4 is based on the [DIGITAfrica Edge AI Blueprint](https://gitlab.inria.fr/digitafrica/blueprints/services/edge-ai-blueprint)
from the DIGITAfrica Horizon Europe project (grant agreement No. 101133297), licensed under CC BY 4.0.

All other lab materials © University of Cape Town, Department of Electrical Engineering.
