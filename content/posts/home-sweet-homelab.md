---
title: "Home Sweet Homelab"
date: 2023-06-06
tags: ["Home Lab"]
hero_image: "https://images.unsplash.com/photo-1521542464131-cb30f7398bc6?w=800&h=400&fit=crop&auto=format&q=80"
---

A few months ago, I really got into the idea of automating my home and monitoring my energy usage. I had previously done some automation and integration of my smart devices, but it was mostly through the respective apps - there wasn't much automation across brands or products.

Then, I jumped in the deep end. I had just decided to get solar panels installed and to trade in my car for an EV, and with that wanted to monitor my home energy usage. After some research, I came across [Home Assistant](https://www.home-assistant.io/), which is able to aggregate data from many different services and take action on that data.

Though the initial idea was to monitor energy usage, I immediately got my raspberry pi out, set up Docker, got Home Assistant running, and integrated my various IoT devices. It was truly like falling down a rabbit hole - one thing lead to another, and before you know it, I now have a dedicated server running [OpenMediaVault](https://www.openmediavault.org/) and over 50 Docker containers.

In addition to Home Assistant and the energy monitoring, I have transformed how I ingest information. I send interesting links to [Wallabag](https://www.wallabag.it/en) to read later; create to-dos in [Vikunja](https://vikunja.io/); save recipes to [Tandoor](https://tandoor.dev/); take quick notes in [Benotes](https://benotes.org/); and write long-form documentation in [BookStack](https://www.bookstackapp.com/). I've even changed (improved) how I keep home records by saving everything important to [Paperless-ngx](https://docs.paperless-ngx.com/).

To support all of these different apps, I have learned quite a bit about setting up and maintaining a server. In particular, I've leaned into Docker and Docker Compose to run the various services; use [Traefik](https://traefik.io/) to route requests and manage SSL certificates; use [Duplicati](https://www.duplicati.com/) to backup each service's data; and use [Technitium](https://technitium.com/) on my local network to provide DNS services. Additionally, I use [WireGuard](https://www.wireguard.com/) and a virtual private server to provide secure, public access to my locally hosted services.

All this to say, I've learned quite a lot in the past few months and am eager to get it down in writing so I don't forget it all! I plan to publish various articles regarding my setup, and as much as I hope it helps someone else, it's also here for my own reference!

So, until next time - happy homelabbing!
