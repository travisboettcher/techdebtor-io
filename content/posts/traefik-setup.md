---
title: "Directing Traefik"
date: 2023-09-02
tags: ["Home Lab"]
hero_image: "https://images.unsplash.com/photo-1465447142348-e9952c393450?w=800&h=400&fit=crop&auto=format&q=80"
---

So - you've set up some fancy new service on your home server that will let you digitize and get rid of that pile of papers that keeps stacking up on top of your file cabinet (instead of actually filing the papers - yay procrastination!). The problem: you can only access said service on `192.168.0.37:8234`. Oh, and now you have 7 other services that you also need to remember the IP and port for.

You might be able to solve part of the problem at the router, or using an internal DNS, but if you have multiple services running on one server, you probably still need to remember multiple port numbers.

Another solution would be to use a reverse proxy - maybe using NGINX, Apache, or HAProxy. The solution I ended up going with was [Traefik](https://traefik.io/traefik/). Traefik allows proxying traffic to your services, using a number of configuration providers. Check out their excellent documentation for a detailed look at the various concepts you can apply to the routing. Below, I will detail my setup and the various configurations and conventions I use.

### Static Configuration

Traefik configuration is broken up between static and dynamic configuration. The static configuration is only loaded once on startup, whereas the dynamic configuration is automatically reloaded as it changes.

The following is my static configuration:

```YAML
# Enables the Traefik API and Dashboard
# Dynamic config also needed to correctly route
api:
  dashboard: true

# Enable the `/ping` health-check endpoint
ping: {}

# Enable prometheus metrics for routers and services
metrics:
  prometheus:
    addRoutersLabels: true
    addServicesLabels: true

# Enable dynamic configuration through
# docker and the file provider
providers:
  docker: {}
  file:
    directory: /etc/traefik/conf
    watch: true

# The entrypoints to listen on
entryPoints:
  # The standard HTTPS port, with a cert resolver
  web:
    address: ":443"
    proxyProtocol:
      trustedIPs: 10.1.10.0/24
    http:
      tls:
        certResolver: lets-encrypt

  # The standard HTTP port, for internal services
  local:
    address: ":80"
    proxyProtocol:
      trustedIPs: 10.1.10.0/24

  # An SFTP endpoint
  sftp:
    address: ":2222/tcp"
    proxyProtocol:
      trustedIPs: 10.1.10.0/24

# The cert resolver for HTTPS, using
# Let's Encrypt and the TLS challenge
certificatesResolvers:
  lets-encrypt:
    acme:
      email: ********
      storage: /etc/traefik/acme/acme.json
      tlsChallenge: {}
```

### Dynamic Configuration

The dynamic configuration defines the routers and services. For the most part, I use the Docker provider, using labels on the containers, as can be seen below:

```YAML
version: '3.8'
services:
  reverse-proxy:
    image: traefik:v2.10
    restart: unless-stopped
    ports:
      - "80:80"
      - "8080:8080"
      - "443:443"
      - "2222:2222/tcp"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik:/etc/traefik
    healthcheck:
      test: traefik healthcheck
      interval: 1m30s
      timeout: 10s
      retries: 3
      start_period: 30s
    extra_hosts:
      - "host.docker.internal:host-gateway"
    labels:
      - "traefik.http.routers.dashboard.rule=Host(`traefik.techdebtor.io`)"
      - "traefik.http.routers.dashboard.service=api@internal"
      - "traefik.http.routers.dashboard.entrypoints=web"
      - "traefik.http.routers.dashboard.middlewares=basic-auth"
      - "traefik.http.middlewares.basic-auth.basicauth.users=${TRAEFIK_BASIC_AUTH}"
      - "traefik.http.routers.dashboard-local.rule=Host(`traefik.techdebtor.local`)"
      - "traefik.http.routers.dashboard-local.service=api@internal"
      - "traefik.http.routers.dashboard-local.entrypoints=local"

  whoami:
    image: traefik/whoami
    restart: unless-stopped
    container_name: whoami
    labels:
      - "traefik.http.routers.whoami.rule=Host(`whoami.techdebtor.io`)"
      - "traefik.http.routers.whoami.entrypoints=web"
      - "traefik.http.routers.whoami-local.rule=Host(`whoami.techdebtor.local`)"
      - "traefik.http.routers.whoami-local.entrypoints=local"
```

One problem I have with my current configuration is the need to define two different routers - one for HTTPS and one for HTTP. I use the two different hostnames to avoid the round-trip cost to hit a server that's on the same network - if I use the `techdebtor.io` host, the device makes a round trip out to my VPS and then back through the wireguard tunnel to my home server; if I use the `techdebtor.local` host, I can access the home server directly. It's on my list though to solve this configuration complexity.

There are a few services I have where I use the file provider - these are either running on other servers or simply not in Docker. An example of a service running on the Docker host is below:

```YAML
http:
  routers:
    omv:
      entryPoints:
        - web
      service: omv
      rule: Host(`omv.techdebtor.io`)
    omv-local:
      entryPoints:
        - local
      service: omv
      rule: Host(`omv.techdebtor.local`)

  services:
    omv:
      loadBalancer:
        servers:
          - url: http://host.docker.internal:8085/
```

Finally, although I use Docker Compose for all my Docker container deployments, I don't configure them all in the same file. This means containers configured in other Compose files need a little more assistance so everything plays nicely together. Note the extra label and network in the following example:

```YAML
version: '3.8'
services:
  dashy:
    image: lissy93/dashy
    volumes:
      - ./config.yml:/app/public/conf.yml
    networks:
      - traefik-net
    expose:
      - 80
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: node /app/services/healthcheck
      interval: 1m
      timeout: 10s
      retries: 3
      start_period: 10s
    labels:
      - "traefik.http.routers.dashy-local.rule=Host(`dashy.techdebtor.local`)"
      - "traefik.http.routers.dashy-local.entrypoints=local"
      - "traefik.docker.network=traefik_default"

networks:
  traefik-net:
    name: traefik_default
    external: true
```

And that's about it to Traefik! If I come across other cool usages or complicated configurations, I'll be sure to write about those, but this is my basic configuration.

#### What am I listening to?

This month, I've been listening to **You Are Who You Hang Out With** by The Front Bottoms.

*(embedded Spotify album)*
