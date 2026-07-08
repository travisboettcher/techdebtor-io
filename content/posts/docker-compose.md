---
title: "Managing Containers with Docker Compose"
date: 2023-09-27
tags: ["Home Lab"]
---

My homelab current consists of about 50 services - 30 or so exposed through Traefik, and then roughly 20 backing services (databases, etc). All of those services run in Docker; all have different lifecycles, requirements, start-up scripts. If I were using barebones Docker, I would probably have 50 scripts lying around to maintain those containers. Instead, I use [Docker Compose](https://docs.docker.com/compose/).

For highly available, self-healing, enterprise-grade services, you probably want something like Kubernetes that can scale and manage your deployment. However, for a homelab and personal use, I really like the dead-simple yet powerful features of Docker Compose. By defining the services in a YAML file (infrastructure-as-code), your entire Docker environment can easily be brought up with one command line:

```
docker compose up -d
```

*(make sure to specify `-d` so Docker doesn't take over your shell...)*

I'll leave the introductory aspects of Docker Compose to the documentation, and below go over some of the tips and tricks I use with Docker Compose.

### Directory structure

By default, Docker Compose uses the current directory to name your services. So, if you discover this like I did, you'll have services named something like `docker-whoami-1`, which resulted from a directory structure like the following:

```
docker/
└─ docker-compose.yml
```

The second part of the name is the name of the service, and the number is just an index.

To better organize things, I've made use of this naming convention and put each Docker Compose file in it's own directory, to help identify the overall purpose of the container:

```
docker/
├── bookstack/
│   └── docker-compose.yml
├── dasky/
│   └── docker-compose.yml
└── traefik/
    └── docker-compose.yml
```

With this structure, my containers have names like `bookstack-app-1`, which makes it really easy to know where to look if something is going wrong!

### Env files

Many containers can be customized using environment variables. The documentation lists a number of ways to pass in the environment variables, but my go-to is using the `env_file` attribute to specify a file containing the environment variables.

```YAML
version: '3'
services:
  bookstack:
    image: lscr.io/linuxserver/bookstack
    env_file: bookstack.env

# the rest left out for brevity
```
*docker-compose.yml*

```
PUID=1000
PGID=1000
APP_URL=http://bookstack.techdebtor.local
```
*bookstack.env*

This is pretty straight-forward, but it allows you to extract those environment variables out of your `docker-compose.yml` file, making it just a bit easier to read.

### Networking

Especially when using Traefik to expose services, there are a few networking-related tips and tricks.

First, if you are organizing the different services using separate `docker-compose.yml` files, those will by default not play nicely together, and you won't be able to reach those services. To address this, you need to explicitly add the service to the same network that Traefik uses, as well as add a label to indicate the network:

```YAML
version: '3'
services:
  bookstack:
    image: lscr.io/linuxserver/bookstack
    networks:
      - traefik-net
    labels:
      - "traefik.docker.network=traefik_default"

networks:
  traefik-net:
    name: traefik_default
    external: true
```

Note that the network is named `traefik-net` here, but references the `default` network from the `traefik` directory (`traefik_default`). The label also needs to reference the actual name and not the alias.

For services that comprise multiple containers, you probably only want to expose one of those through Traefik - but you also need those services to continue to talk to eachother. I won't deep dive into container networking here, but one of the coolest things about these container environments is the ability to isolate and sandbox services. By taking advantage of the standard Docker Compose syntax, you can include the 'exposed' service in both the Traefik network and the network that the dependent services are on:

```YAML
version: '3'
services:
  bookstack:
    image: lscr.io/linuxserver/bookstack
    networks:
      - traefik-net
      - default
    labels:
      - "traefik.docker.network=traefik_default"

  db:
    image: lscr.io/linuxserver/mariadb
    labels:
      - "traefik.enable=false"

networks:
  traefik-net:
    name: traefik_default
    external: true
```

There are a few differences from the previous example:

- The `bookstack` service is now included on two networks, `traefik-net` that references the external Traefik network; and `default`, which is the default network created for the service.
- The `db` service does not include a `networks` attribute - it will join the `default` network.
- The `db` service also has a label to disable Traefik - this just indicates to Traefik that it should not try to expose the `db` service.

There are many other small tricks I've come across, but what I've covered above are probably the three top suggestions I have based on my experience with Docker Compose so far. As I continue to experiment and tweak my setup, I plan to document smaller, one-off tricks, so you can look forward to those.

#### What am I listening to?

There are a bunch of podcasts I want to recommend, but today I'll highlight what is definitely my favorite: A Problem Squared. Two comedians take peoples' problems and try to provide a solution - sometimes the solution is even decent! Every episode brings me so much joy, and I immediately move new episodes to the top of my queue.

*(embedded Spotify podcast show)*
