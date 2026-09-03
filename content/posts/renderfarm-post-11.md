---
title: "[RenderFarm] Post 11"
date: 2013-09-26T14:27:39+00:00
tags: ["[RenderFarm]"]
summary: "And so it begins continues. This is the first official [RenderFarm] post since I went to Madison I believe. A new semester has begun and so too begins my work…"
draft: true
archive_url: "https://web.archive.org/web/20141101181311/http://futurecyb.org/?p=186"
archive_source: "futurecyb.org"
---

And so it ~~begins~~ continues. This is the first official [RenderFarm] post since I went to Madison I believe. A new semester has begun and so too begins my work on the project. This semester I am going to focus on two main goals:

  1. I want to have a front-end web service available to the art students on campus before I graduate; and
  2. I want DSABR to work with Maya as well as Blender.



The second goal is really just as important (if not more so) than the first: if DSABR doesn’t work with Maya, it will most likely get very little use since Maya is the standard software for the art department.

To accomplish these goals, I have joined forces with another student. This student will be focusing on the web service and I will be focusing (at least for now) on polishing DSABR and implementing new, useful features.

On that note, here are several things I accomplished in the past week:

  * I created a man page to provide easy-to-read documentation and an example of how to use the script, now called dsabr.py;
  * I added a command line flag to allow for a batch mode – this will be used when calling the script from the web service;
  * I added a command line argument to allow the user to specify the name of the project being rendered – again to be used by the web service; and finally,
  * I reformatted the script to conform to the PEP8 python standard.



There are still a lot of tasks on my plate. In addition to getting DSABR to work with Maya, I need to:

  * provide exit codes and correctly handle errors (This will be especially necessary for when I’m not the only one using the script!);
  * research implementing a RESTful web service; and, to supplement the batch mode,
  * create a log file with more useful information in it than the current log file.



With any luck (and what could be a good amount of work), all these tasks will be done and there will be an Alpha or Beta version of the DSABR web service up and running, ready for art students to take advantage of!

One last note: the mercurial repository for the project is located [here](https://bitbucket.org/tboettcher/dsabr).
