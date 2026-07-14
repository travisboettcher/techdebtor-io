---
title: "Replacing Google Photos"
date: 2023-10-18
tags: ["Home Lab"]
hero_image: "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=800&h=400&fit=crop&auto=format&q=80"
---

One of my goals as I've been working on my homelab has been to replace Google Photos. For me, there have been main reasons to find an alternative:

1. Privacy - more and more I dislike the idea of my photos being hosted somewhere I don't control
2. Space - I'm starting to hit the limit of free storage on Google Photos

As a replacement, I wanted something that provided some of the same features I've come to know and love about Google Photos, but in a self-hosted format:

- Simple integration with my phone, so photos are immediately backed up and accessible in the cloud
- Facial recognition and other photo categorization features so I'm able to easily search through photos

With those requirements in mind, I've been trying out a few different self-hosted options. I tried out [Lychee](https://lycheeorg.github.io/), [Piwigo](https://piwigo.org/), and [PhotoPrism](https://photoprism.org/), which each offered something a little different. For the time being though, I've landed on PhotoPrism - it seemed the most robust of the three, with an intuitive interface and the photo management and search features I was looking for.

There is a pretty good ["Getting Started" guide](https://docs.photoprism.app/getting-started/docker-compose/), which includes instructions for Docker Compose. Other than adding Traefik labels for routing, my setup is pretty much the default setup.

After getting it set up, I used [Google Takeout](https://takeout.google.com/) to export all my photos. It did take a couple days before I got all the files, and then downloading the roughly 200GB and extracting that also took some time! Once that is done, you can [add those files directly to PhotoPrism](https://docs.photoprism.app/user-guide/use-cases/google/). (I didn't do this for some reason I can't exactly remember - instead there was a script I ran to reorganize the photos first, and then I imported them - that was probably more difficult than it needed to be)

So that's one part of the equation done - existing photos are now imported into a self-hosted photo management tool, and once they've indexed, you can search by label, and it will automatically identify people too! It's not quite as robust as Google - it has a really hard time identifying small kids - but for the most part I'm pretty happy with it!

In addition to that, I feel more in control of my data - I know where it's sitting and how it's encrypted. I also am able to control how the photos are backed up - more on [Duplicati](https://www.duplicati.com/) in a future post!

There's still a missing piece though - how to upload new photos from my phone, automatically. PhotoPrism doesn't have an app or anything, but they do support WebDAV, which allows you to upload photos from any app that also supports WebDAV. On Android, my current go-to is FolderSync - once configured to talk to PhotoPrism, I am able to select which folders on my phone to watch and when to sync the photos. I have it sync photos once a day, which isn't ideal since the photos aren't uploaded to the cloud instantaneously, but it's good enough for now.

So that's my "Google Photos" replacement! It's definitely still a little rough around the edges, and I haven't convinced my wife to convert, which means I'm still using Google Photos as well, but it feels good knowing I have a working solution for when I'm ready to really jump ship.

#### What am I listening to?

In the last year or so, there has been a huge surge in interest in AI, and specifically LLMs (Large Language Models). Although I have taken several courses on AI, ML, and NLP, the field has moved fast enough I felt a bit out of the loop. In an attempt to catch up, I've started to listen to a couple AI-centric podcasts, both of which I've really come to enjoy.

The one I want to highlight today is [Data Skeptic](https://dataskeptic.com/). In the latest season, entitled "Machine Intelligence", the host Kyle Polich talks with various experts in the field. Each guest brings a unique perspective and some really interesting research is discussed - both pushing the boundaries of technologies like LLMs, and highlighting the dangers of putting too much trust and rushing too quickly to market with those same ill-understood technologies.

*(embedded Spotify podcast episode)*
