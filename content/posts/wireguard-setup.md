---
title: "How I access my home network"
date: 2023-07-09
tags: ["Home Lab"]
hero_image: "https://images.unsplash.com/photo-1543946602-a0fce8117697?w=800&h=400&fit=crop&auto=format&q=80"
---

One of the projects I've wanted to tackle for a long time was to implement a way to access my home network from anywhere. There are a bunch of ways to tackle this, including just port forwarding at the router. However, I had a few requirements:

- Didn't want to have to use an IP (and look up my home IP when it changes)
- Should be secure, so that not just anyone can access my network
- Should be simple enough to configure and modify

For the first requirement, I could have used a Dynamic DNS service - in fact, my ASUS router comes with a built-in service. This would have allowed me to access my home network with a domain name (or `asuscomm.com` subdomain).

The problem I had with this solution though was that anyone using the domain name would also be hitting my home network directly. This didn't feel secure (although I'm sure it can be), and just felt wrong - an invasion of privacy, almost.

### WireGuard enters the ring

In looking for options, I came across the new VPN on the block, [WireGuard](https://www.wireguard.com/). A VPN would solve my security concerns, as I could configure my home network to only allow connections within the VPN.

But this led to a new, previously unknown requirement - what if there are some resources I want anyone to access? For example, what if I want to share a file stored on my home network with a friend? Restricting traffic to a VPN is secure, but would require opening up the VPN to others and excludes opening any resources to an anonymous user.

That's when I found Jake Howard's blog, [theorangeone.net](https://theorangeone.net/). On his blog, there were two posts in particular that led me to my current setup:

- https://theorangeone.net/posts/wireguard-getting-started/
- https://theorangeone.net/posts/wireguard-haproxy-gateway/

Please read those for the details, but at a high level, the posts outline using [HAProxy](https://www.haproxy.org/) as a public gateway located on a VPS, directing traffic over WireGuard to the home network. This setup allows for a secure connection to my home network, but also allows me to publicly share resources as needed, solving two requirements. The public-facing gateway means I can make use of DNS and a hostname, solving the first requirement.

And, as you'll see below, using WireGuard and HAProxy provides a simple configuration that is easily updated.

### Finally, the good stuff

I'll leave the basic setup of WireGuard for other articles, including the first post linked above, and here I will just share my configuration, including an explanation of some of the options I've included.

#### Server - WireGuard config

```
[Interface]
Address = 10.1.10.1
PrivateKey = <server private key>
ListenPort = 51820

[Peer]
PublicKey = <client public key>
AllowedIPs = 10.1.10.2/32

[Peer]
PublicKey = <client public key>
AllowedIPs = 10.1.10.3/32

[Peer]
PublicKey = <client public key>
AllowedIPs = 10.1.10.4/32

[Peer]
PublicKey = <client public key>
AllowedIPs = 10.1.10.5/32
```

This is the configuration on the VPS. Since it is the one node in the network with a known/discoverable IP address, all peers (clients) will connect to it to join the VPN. The `Interface` section of the config is pretty standard, with the address of the node on the VPN (`10.1.10.1`), the private key, and the port to listen on.

The `Peer` sections only need to include the peer's public key and the IP that that peer is going to be using within the VPN. This instructs WireGuard to accept traffic from the peer on that IP, and also to direct outgoing traffic for that IP to the peer.

#### Client - WireGuard config

```
[Interface]
Address = 10.1.10.3
PrivateKey = <client private key>
ListenPort = 21841

[Peer]
PublicKey = <server public key>
Endpoint = <server hostname>:51820
AllowedIPs = 10.1.10.0/24
```

Since WireGuard doesn't really have a concept of server and client, only peers, the "client" configuration is quite similar to the "server" configuration above. The key differences are in the `Peer` section. In addition to the public key and the allowed IPs, an endpoint is also specified. This is the hostname and port of the server node, which WireGuard will use to initiate the connection.

Also notice that the `AllowedIPs` IP mask is slightly different. Rather than *just* the IP the server will use on the VPN, we direct all traffic on the VPN through the server.

#### Server - HAProxy config

```
###
# Global and defaults left out for brevity
###

listen http
  bind *:80
  mode http
  http-request redirect scheme https

listen https
  bind *:443
  mode tcp
  server default 10.1.10.3:443 send-proxy
```

Finally, on the server, we use HAProxy as a gateway. With the above configuration, the server listens for traffic on both port 80 (HTTP) and 443 (HTTPS). Traffic on port 80 is redirected to HTTPS, and traffic on 443 is proxied over the WireGuard network to the server on my home network. This setup allows me to expose services for public consumption, and for other services I can access them using the WireGuard network.

In a future post, I'll discuss my Traefik setup, which allows me to selectively proxy traffic to various services.

---

#### What am I listening to?

Occasionally, I'll throw something at the bottom of posts, highlighting some recommendation to read, listen to, or play. For this post, I'm including **What Matters Most** by Ben Folds. Since it was released, the album has been playing on repeat around the house.

*(embedded Spotify album)*
