---
title: "[RenderFarm] Post 7"
date: 2013-03-25T01:45:54+00:00
tags: ["[RenderFarm]"]
summary: "After a slight break from working on the RenderFarm project (to work on other projects/midterms), I got back at it today. Most of the progress I made is thanks…"
draft: true
archive_url: "https://web.archive.org/web/20130925002818/http://futurecyb.org/?p=121"
archive_source: "futurecyb.org"
---

After a slight break from working on the RenderFarm project (to work on other projects/midterms), I got back at it today. Most of the progress I made is thanks to Dr. Bui’s own contributions, but I’ll still claim the implementation of his work as my own :P So, the small progress that was made:

  * The call to FFMPEG is now made with the subprocess module’s Popen and piping the temporary files in with Python functions. This used to be done all with one subprocess.call(), but this was pointed out to be inefficient/poor programming. It is much better now.
  * Using a shell script cooked up by Bui, we can now render frames at remote sites (via flocking). The current implementation seems to ignore our own nodes and only uses the ones in Madison though, so more work needs to be done.



Using 80 workers (all on Madison’s cluster), I was able to render 500 frames in about 3 minutes. I haven’t done any other testing, so I don’t know if that is an improvement, but it felt good to see it working and the final movie to come out right!

Future work to be done:

  * I need to figure out a way to use the local cluster AND the Madison cluster. I’m not sure if this is a side-effect of Bui’s script or something in my code, but it should be fixed.
  * Although the tar file is cached so that it isn’t transfered to Madison with each task, currently each task untars the Blender tarball and does some voodoo magic to make it executable. I want to see if there’s a way to eliminate this.
  * I currently do not check to see if Blender is installed on the machine the task is working on. When we get to a point where the task MAY be working on a machine with Blender installed, we will need to decide if it is worth it to make this check (I don’t know how hard it would be to modify the code to work both ways).
  * Tests! I need to get to work on testing the performance of this program now that flocking is partially working.
