# Lab 1 — Introduction to Containers

**Day 1 · Monday 9 March 2026 · 14:00–16:30**

---

## Overview

This lab introduces Docker containers and container networking from the ground up. Everything you do here underpins the later labs: in Lab 2 the entire OAI 5G core runs as Docker containers on a shared network, and in Lab 3 the O-RAN RIC is orchestrated with Docker Compose.

**Duration:** 2.5 hours  
**Terminals needed:** 1–2

## Learning objectives

- Pull, run, inspect, and remove Docker containers
- Explain image layering and write a `Dockerfile`
- Configure custom bridge networks and understand DNS-based service discovery
- Orchestrate a multi-container application with Docker Compose

## Prerequisites

- [ ] `docker run hello-world` succeeds  
- [ ] `docker compose version` returns v2.x.x  
- [ ] Basic Linux command-line comfort

---

## Part 1 — Docker fundamentals

### 1.1 Your first container

```bash
docker run hello-world
```

Docker first looks for the image locally, then pulls it from Docker Hub. Read the output — it explains exactly what happened.

### 1.2 Interactive Ubuntu container

```bash
docker run -it --name myubuntu ubuntu:22.04 /bin/bash
```

Inside the container:

```bash
cat /etc/os-release
hostname
apt update && apt install iproute2
ip addr show
exit
```

The container has its own hostname and network interface, isolated from the host.

### 1.3 Container lifecycle

```bash
docker ps -a                          # all containers (running and stopped)
docker start myubuntu
docker exec -it myubuntu bash         # attach to running container
exit
docker stop myubuntu
docker rm myubuntu
docker images                         # locally cached images
```

> **Q1** — When you ran `ip addr show` inside the container, what IP address and interface name did you see? How does this differ from your host machine?

---

## Part 2 — Building custom images

### 2.1 Write a Dockerfile

```bash
mkdir ~/lab1_webserver && cd ~/lab1_webserver

cat > Dockerfile << 'EOF'
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY index.html /app/index.html
EXPOSE 8080
CMD ["python3", "-m", "http.server", "8080"]
EOF

echo '<h1>Hello from EEE5138Z!</h1>' > index.html
```

Build and run:

```bash
docker build -t eee5138-web:v1 .
docker run -d -p 8080:8080 --name webserver eee5138-web:v1
curl http://localhost:8080
```

### 2.2 Inspect image layers

```bash
docker history eee5138-web:v1
```

Each line is a layer. Base layers are shared among all containers using `ubuntu:22.04`.

> **Q2** — How many layers does your image have? Which layer consumes the most space? Why is it better to combine `RUN apt-get update && apt-get install` into one `RUN` instruction rather than two separate ones?

---

## Part 3 — Container networking

### 3.1 List default networks

```bash
docker network ls
docker network inspect bridge
```

Note the subnet (`172.17.0.0/16` by default) and gateway.

### 3.2 Create a custom bridge network

```bash
docker network create \
  --driver bridge \
  --subnet 192.168.100.0/24 \
  lab1_net

docker network inspect lab1_net
```

### 3.3 DNS-based container discovery

Start two containers on your custom network:

```bash
docker run -d --name node1 --network lab1_net ubuntu:22.04 sleep 600
docker run -d --name node2 --network lab1_net ubuntu:22.04 sleep 600
```

Install ping in node1, then ping node2 **by name**:

```bash
docker exec node1 bash -c \
  'apt-get update -qq && apt-get install -y -qq iputils-ping'
docker exec -it node1 ping -c 4 node2
```

Docker's embedded DNS resolves `node2` to its IP. This is exactly how the OAI AMF, SMF, and UPF find each other in Lab 2.

Now repeat on the **default bridge network** (no `--network lab1_net`):

```bash
docker stop node1 node2 && docker rm node1 node2

docker run -d --name node1 ubuntu:22.04 sleep 600
docker run -d --name node2 ubuntu:22.04 sleep 600
docker exec node1 bash -c \
  'apt-get update -qq && apt-get install -y -qq iputils-ping'
docker exec -it node1 ping -c 4 node2 || echo "FAILED — no DNS on default bridge"
```

> **Q3** — On the custom network, what IP did `node2` resolve to? On the default bridge, does `ping node2` succeed? Explain the difference — what Docker feature is responsible?

Cleanup:

```bash
docker stop node1 node2 && docker rm node1 node2
docker network rm lab1_net
```

---

## Part 4 — Docker Compose

### 4.1 Define a two-service application

```bash
mkdir ~/lab1_compose && cd ~/lab1_compose

cat > docker-compose.yml << 'EOF'
version: '3.8'

networks:
  app_net:
    driver: bridge
    ipam:
      config:
        - subnet: 10.100.0.0/24

services:
  redis:
    image: redis:7-alpine
    networks: [app_net]
    ports: ["6379:6379"]

  monitor:
    image: ubuntu:22.04
    networks: [app_net]
    depends_on: [redis]
    command: >
      bash -c "apt-get update -qq &&
               apt-get install -y -qq redis-tools &&
               sleep 5 &&
               redis-cli -h redis ping"
EOF
```

Deploy:

```bash
docker compose up -d
docker compose ps
docker compose logs monitor
```

The monitor connects to `redis` by container name and prints `PONG`.

### 4.2 Teardown

```bash
docker compose down
docker stop webserver 2>/dev/null; docker rm webserver 2>/dev/null
docker system prune -f
```

> **Q4 (design)** — In a 5G core, the AMF, SMF, and UPF communicate over N2/N11 and N4 interfaces. Sketch a `docker-compose.yml` skeleton — just `services:` and `networks:` — that would deploy these three functions on a shared network called `5gc_net`. Use placeholder images (e.g., `image: 5gc/amf:latest`). Include the SCTP port AMF listens on for gNB connections (hint: NGAP uses port **38412**).

---

## Submission

Compile answers to **Q1–Q4** into a single PDF or Word document.  
Include your name, student number, and relevant screenshots.  
**Deadline: Friday 13 March 2026, 17:00 via the course submission portal.**

---

*Next → [Lab 1: SDN with Mininet](../lab2-mininet/)*
