# Lab 2 — SDN with Mininet

**Day 2 · Tuesday 10 March 2026 · 14:00–16:30**

---

## Overview

Software-Defined Networking (SDN) separates the **control plane** (deciding where traffic goes) from the **data plane** (moving packets). A central controller installs flow rules into switches via **OpenFlow**. This lab builds your understanding from first principles: you start with raw flow table manipulation, then use a real SDN controller to implement progressively smarter forwarding logic.

**Duration:** 2.5 hours  
**Terminals needed:** 2–3

## Learning objectives

- Build and explore virtual topologies with Mininet
- Inspect and manually populate OpenFlow flow tables with `dpctl`
- Understand the difference between hub, learning switch, and firewall behaviour
- Implement and trace a POX hub and L2 learning switch
- Implement a Layer-2 firewall policy using POX

## Prerequisites

- [ ] `sudo mn --test pingall` → 0% dropped
- [ ] POX cloned: `ls ~/pox/pox.py` returns the file
- [ ] Wireshark installed and user in `wireshark` group
- [ ] Basic Python 3 familiarity

> **Helpful reading (optional):** [Introduction to Mininet](https://github.com/mininet/mininet/wiki/Introduction-to-Mininet)

---

## Part 1 — Flow tables with the default controller

The default Mininet controller implements a **learning switch** internally. We will first explore flow tables before attaching any external controller.

### 1.1 Launch a simple topology

```bash
sudo mn -c                                      # clean up any previous state
sudo mn --topo single,3 --switch ovsk
```

This creates switch `s1` with three hosts `h1`, `h2`, `h3`.

### 1.2 Inspect ports

```
mininet> dpctl show
```

`dpctl` lets you query and modify switch state directly. Note the port numbers listed for each host interface.

### 1.3 Inspect flow table — before any traffic

```
mininet> dpctl dump-flows
```

> **Question 1:** There are no flow entries. Why is this the case?

### 1.4 Generate traffic, then inspect again

```
mininet> h1 ping h2 -c 3
mininet> dpctl dump-flows
```

> **Question 2:** Flow entries now appear. Explain why they were installed and what each field (`in_port`, `actions`, …) means.

---

## Part 2 — Remote controller mode

Now we act as the controller ourselves by adding flow entries manually.

### 2.1 Restart with a remote controller

```
mininet> exit
```

```bash
sudo mn --topo single,3 --mac --switch ovsk --controller remote
```

The `--controller remote` flag tells the switch to connect to an OpenFlow controller on `127.0.0.1:6633`. Since nothing is listening there yet, the switch has no forwarding instructions.

### 2.2 Try pinging — observe the failure

```
mininet> h1 ping h2 -c 3
mininet> dpctl dump-flows
```

> **Question 3:** There are no flow entries even after a ping. Why?

### 2.3 Add flow entries manually (acting as the controller)

```
mininet> dpctl add-flow in_port=1,idle_timeout=1000,actions=output:2
mininet> dpctl add-flow in_port=2,idle_timeout=1000,actions=output:1
mininet> dpctl dump-flows
mininet> h1 ping h2 -c 3
```

You have just done what a real controller does: instructed the switch how to forward packets.

---

## Part 3 — POX hub

POX is a Python-based SDN controller. We will use its built-in hub and learning switch implementations to understand controller logic.

### 3.1 Restart topology

```
mininet> exit
```

```bash
sudo mn --topo single,3 --mac --switch ovsk --controller remote
```

### 3.2 Start the POX hub controller

Open a **second terminal** and run:

```bash
cd ~/pox
./pox.py forwarding.hub
```

A **hub** floods every packet out of every port. Open `pox/forwarding/hub.py` and review the `_handle_ConnectionUp(event)` function.

> **Question 4:** What logic does `_handle_ConnectionUp` implement? Why does it install a single wildcard flow entry rather than per-host entries?

Back in the Mininet terminal:

```
mininet> dpctl dump-flows
mininet> pingall
```

Observe the single catch-all flow entry that floods all traffic.

---

## Part 4 — POX L2 learning switch

### 4.1 Stop POX and restart the topology

In the POX terminal press `Ctrl-C`, then:

```
mininet> exit
```

```bash
sudo mn --topo single,3 --mac --switch ovsk --controller remote
```

Second terminal:

```bash
cd ~/pox
./pox.py forwarding.l2_learning
```

Open `pox/forwarding/l2_learning.py` and review the `_handle_PacketIn` function.

### 4.2 Observe flow table evolution

Run `dpctl dump-flows` **before**, **during**, and **after** a ping:

```
mininet> dpctl dump-flows          # before — should be empty
mininet> h1 ping h2 -c 3
mininet> dpctl dump-flows          # after — per-host entries appear
```

> **Question 5:** Explain the L2 learning switch behaviour. How does it differ from the hub? What is the role of `packet_in` messages and when do they stop being generated?

---

## Part 5 — Layer-2 firewall

You will now implement a POX firewall that **blocks traffic between two specific hosts** while allowing all other traffic.

Follow the tutorial at:

> http://www.anshumanc.ml/networks/2017/09/19/firewall/

The tutorial walks you through creating a new POX component (`pox/ext/firewall.py`) that:

- Reads a policy from a CSV file (`firewall-policies.csv`)
- On switch connection, installs DROP rules for blocked host pairs
- Allows all remaining traffic to proceed normally

### 5.1 Implement and test the firewall

Create your policy CSV and implement `pox/ext/firewall.py` following the tutorial. Then test:

```bash
./pox.py misc.firewall --policy=firewall-policies.csv
```

```
mininet> pingall
```

> **Question 6:** Include your final `firewall.py` source code and your `firewall-policies.csv`. What OpenFlow priority did you use for the DROP rules, and why does priority matter when you also want to allow other traffic?

---

## Submission

Write a lab report containing:

- Answers to Questions 1–6
- Your final `firewall.py` source code
- Screenshot of the final `pingall` output showing which pairs are blocked

Submit via the course portal by **Friday 13 March 2026 at 17:00**.

---

## Navigation

← [Lab 1 — Containers](../lab1-containers/README.md) · [Lab 3 — 5G SA Network](../lab3-5g-oai/README.md) →
