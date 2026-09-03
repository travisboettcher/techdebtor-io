---
title: "[RenderFarm] Post 8"
date: 2013-04-05T15:05:15+00:00
tags: ["[RenderFarm]"]
summary: "The past week and a half have seen some major improvements to the RenderFarm project! Each worker now downloads the Blender tarball from a UWEC server, unpacks…"
draft: true
archive_url: "https://web.archive.org/web/20130925001225/http://futurecyb.org/?p=144"
archive_source: "futurecyb.org"
---

The past week and a half have seen some major improvements to the RenderFarm project!

  * Each worker now downloads the Blender tarball from a UWEC server, unpacks it and makes a wrapper so it can be executed. This final product is cached and reused for each worker’s subsequent tasks in a job.
  * Using condor_submit_rhel6_workers, we can render on local UWEC machines AND we can flock over to Madison if we need to.
  * The call to FFMPEG has been modified once again. It now includes to subprocesses – one for FFMPEG and one for a helper script that controls the flow of the incoming temp files’ contents. This was necessary to fix a broken pipe error we received when rendering a large number of frames.
  * We now make use of a WQ function activate_fast_abort() to cull straggling workers. If a worker takes longer than the average worker’s time multiplied by some given multiplier, the worker is removed and the task is resubmitted. This fixed a major problem I had when rendering a large number of frames (>1000) – one or more workers would just seem to sit there and not complete, causing the entire process to come to a stop.



In addition to the functional changes, I have also started timing the process to see what kind of improvements have been made. Here are some preliminary results:

  * If we eliminate the time it takes to connect to a worker, it takes about 16 seconds to render one frame with one worker. This is a good indication of how long it takes to download the blender tarball, unpack it, and wrap it up as rendering one frame and stitching it to nothing with FFMPEG should both take very little time.
  * On the other extreme, it took one worker 70.2 minutes to render 10000 frames (~5 and a half minutes of movie). That averages to 2.4 frames per second. In comparison, it took 100 workers (max 95 connected workers) 6.4 minutes to render the same movie. That’s 26 frames per second!



Something I’ve noticed from the results I’m getting is that more workers do not always equal better performance. For example, in rendering 100 frames it was better to use 10 workers than to use 100 – or even 15 – workers. And in the above example with 10000 frames, 6.4 minutes is a good improvement over 70.2 minutes, but it’s not as good as a linear improvement. So the next thing to do is to collect enough data to be able to predict the correct number of workers for a give job.

Other things to do:

  * Print out some statistics when the job is complete: name of the movie, number of frames rendered, max number of workers, time it took, frames rendered per second.
  * Make sure target movie doesn’t already exist.
  * Make a check to see if completed tasks are successful. If a task is not successful, resubmit the task.
