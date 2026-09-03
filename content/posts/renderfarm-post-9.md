---
title: "[RenderFarm] Post 9"
date: 2013-04-12T14:34:22+00:00
tags: ["[RenderFarm]"]
summary: "A short update today as I try to solidify the code for testing. The minor changes include: Adding a printout upon completion. The printout includes: the output…"
draft: true
archive_url: "https://web.archive.org/web/20130925002431/http://futurecyb.org/?p=147"
archive_source: "futurecyb.org"
---

A short update today as I try to solidify the code for testing. The minor changes include:

  * Adding a printout upon completion. The printout includes: the output filename; the number of frames rendered; start and end times; and the max number of connected workers.
  * Forcing FFmpeg to overwrite the output movie file if it already exists.



The rest of my time has been spent running tests and collecting data. My data set is about 350 large, but I still need more! I am currently testing the performance of rendering movies with thousands of frames (1000..10,000) and the impact flocking to Madison has on the render time. Currently I see a hard peak performance at 32 – 36 workers for all projects in this frame range (which is to be expected as this is the number of local workers available). I would like to see how many, if any, flocking workers consistently performs better.
