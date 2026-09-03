---
title: "[RenderFarm] Post 6"
date: 2013-03-08T15:07:12+00:00
tags: ["[RenderFarm]"]
summary: "This week SimCity 5 came out so I got nothing done. Or at least that would be my post if their servers had been able to stand up to the demand! Stupid…"
draft: true
archive_url: "https://web.archive.org/web/20130925005405/http://futurecyb.org/?p=113"
archive_source: "futurecyb.org"
---

This week SimCity 5 came out so I got nothing done.

Or at least that would be my post if their servers had been able to stand up to the demand! Stupid always-online DRM!

So, I did get some done this week, but nothing too exciting. I made changes to the command line arguments:

  * I added –log and –debug arguments;
  * –output now takes the filename with extension;
  * if –log is set, both blender.log and workqueue.log are produced;
  * and –format now specifies the intermediate image filetype as opposed to the output’s filetype.



The only other thing I changed was the progress bar: it now shows the number of workers connected and the number of tasks running.

The next thing I need to do is change the way I use FFmpeg. I currently have a complex command that includes piping the output of `cat` to `ffmpeg` being called with `subprocess.call()`. I need to rewrite this using `subprocess.Popen()` and `subprocess.PIPE`. After that is finished, barring minor tweaks, I should be ready to start testing the performance!
