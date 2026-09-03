---
title: "[RenderFarm] Post 5"
date: 2013-03-01T09:26:04+00:00
tags: []
summary: "I didn’t find a lot of time in the past week to dedicate to this project, so I haven’t accomplished a whole lot. The main feature I worked on generates the…"
draft: true
archive_url: "https://web.archive.org/web/20130925005608/http://futurecyb.org/?p=84"
archive_source: "futurecyb.org"
---

I didn’t find a lot of time in the past week to dedicate to this project, so I haven’t accomplished a whole lot. The main feature I worked on generates the temp files’ path names in the form `tempdir + '/%d/%d/temp_%04d.png'`, where `tempdir` is the directory given by Python’s tempfile module and `'/%d/%d/temp_%04d.png'` is based on the frame number being saved. This will allow more files to be generated without bogging down the filesystem, as it only allows 100 frames per folder.

The trick to making this work with FFmpeg (since there is no longer just one directory containing all the images) is to generate a text file containing all the image file paths. These need to be in sequential order (i.e. the path for image temp_0042.png must come directly after the path for temp_0041.png), but then with some command line magic you can pipe the images to FFmpeg and get the resulting movie out.

The other task I started working on was using the logging module. I need to generate two log files – one for WorkQueue-related things and one for Blender-related things. Currently there is a blender.log generated containing the command, result, and hostname of each Blender task submitted. That’s as far as I got as I can’t figure out how to redirect WorkQueue’s debugging from printing to the console to printing to a log file.
