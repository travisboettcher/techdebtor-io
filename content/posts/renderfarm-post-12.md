---
title: "[RenderFarm] Post 12"
date: 2013-11-21T04:11:45+00:00
tags: ["[RenderFarm]"]
summary: "It’s been a while since I’ve logged into this site! The first thing I learned after logging in is that I have about 9 pending updates to WordPress and various…"
draft: true
archive_url: "https://web.archive.org/web/20141102104304/http://futurecyb.org/?p=198"
archive_source: "futurecyb.org"
---

It’s been a while since I’ve logged into this site! The first thing I learned after logging in is that I have about 9 pending updates to WordPress and various plug-ins, all of which I am actively ignoring right now. The second thing I learned is that I haven’t made very much (any) progress on DSABR since the end of September. I knew it had been a while, but that’s kind of sad. To be fair, it has been a busy semester – but still!

I believe an update on including Maya in DSABR is in order. The current status is… it’s a no-go. I attempted to get a local worker started and rendering an image on the Windows machines that Maya is installed on and it kept giving me an error. Both debugging and consulting other people failed in coercing Windows to let me render a Maya file with Work Queue. So that is at a standstill right now – several Windows machines are getting HTCondor installed on them, so hopefully that will allow us to use Maya.

Anyway, I’ve made minute progress tonight 😀 In addition to changing the command line interface to accept start and end frames last week, tonight I’ve implemented the batch file output. If the user chooses batch mode, all output to stdout is turned off and instead DSABR writes out several useful pieces of JSON-formatted information. I chose JSON simply because I feel like it is an easily parse-able, well-known format.

The current keys included in the JSON are: timestamp, elapsedTime, workersConnected, tasksRunning, and currProgress (the number of frames completed). I believe this is sufficient for our purposes, but obviously it might need some tweaking.

Other than the batch mode and file, I updated the man page and example_workflow.sh to reflect the new command line interface. John (the student creating the website that will allow students to easily access DSABR) and I met up last week to go over what he needs to collect from the user in order to call my script. Because Maya is not working right now, his interface will only be concerned with the parameters I need to render a Blender file – if I get Maya working, we can easily add in form elements to collect the other information.
