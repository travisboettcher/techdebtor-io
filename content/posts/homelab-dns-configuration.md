---
title: "Homelab DNS Configuration"
date: 2025-08-09
---

I've previously discussed [how I route external traffic to my homelab](/posts/wireguard-setup/) and [how I route traffic that has reached my homelab](/posts/traefik-setup/). One outstanding issue was the following: I wanted to be able to have internal-only resources, accessible only locally or through a VPN, along side my externally visible resources (like this blog!). In addition to the privacy of internal-only resources, I wanted to reduce traffic through my VPS. One example is Jellyfin - I didn't want local traffic to route out to my VPS, only to be routed back to my homelab to stream movies.

### The Initial Workaround

I solved these issues temporarily by using two different domains: `techdebtor.io` and `techdebtor.local`. However, this posed a a different issue that I still wanted to address: I was forced to either use a self-signed certificate for SSL or not use SSL at all - I opted for `http://techdebtor.local` because in my view, having to install a certificate on each device to be able to trust the service wasn't really worth it. Using an insecure connection resulted in some issues itself - in particular, some clients did not support connecting via http.

### The Requirements

So, I set out to finally solve this networking issue with the following requirements:

- Internal resources can only be accessed locally or via VPN
- Traffic to internal resources stays local
- Support SSL certificates, using Traefik's ability to automatically issue certificates

### The Solution Journey

I initially considered purchasing a different domain - this would have worked, but didn't feel as elegant, so I ditched the idea pretty quickly.

What I really wanted to do was have subdomains like `https://example.internal.techdebtor.io`. This would continue to use Traefik's configuration to issue certificates for `techdebtor.io` subdomains, solving that issue. However, with how I have public DNS configured (a wildcard CNAME, to allow spinning up new subdomains quickly), this meant traffic would still get routed to my homelab.

### The Final Architecture

What I landed on was the following:

- **Public blackhole**: DNS entry 0.0.0.0 for `internal.techdebtor.io` publicly
- **Local DNS zones**: a Primary DNS Zone for `internal.techdebtor.io`, with an A record pointed to my homelab server locally; and a Forwarder DNS Zone for `techdebtor.io` forwarding to Vultr's nameservers, where I have my primary `techdebtor.io` DNS entries.
- **Security layer**: IP allow list blocking any non-local IPs

### The Result

This setup gives me exactly what I wanted: internal services accessible at clean URLS like `jellyfin.internal.techdebtor.io` with proper SSL certificates, while ensuring that traffic never leaves my local network. The split DNS Configuration means that:

- External users can't resolve `internal.techdebtor.io` subdomains (they get `0.0.0.0`)
- Local users get the correct internal IP addresses
- Traefik can still issue valid Let's Encrypt certificates for the `*.internal.techdebtor.io` subdomain
- All traffic stays local, reducing load on my VPS and improving performance

The beauty of this approach is that it leverages the existing domain structure while maintaining the security and performance benefits I was looking for. No additional domain purchases needed, and the configuration is relatively straightforward once you understand the split DNS concept.
