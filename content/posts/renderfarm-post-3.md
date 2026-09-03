---
title: "[RenderFarm] Post 3"
date: 2013-02-15T09:21:28+00:00
tags: []
summary: "I started in full on creating the RenderFarm program this past week. Utilizing WorkQueue and the subprocess and tempfile modules, I started modifying the…"
draft: true
archive_url: "https://web.archive.org/web/20160731042642/http://futurecyb.org/?p=70"
archive_source: "futurecyb.org"
---

I started in full on creating the RenderFarm program this past week. Utilizing WorkQueue and the subprocess and tempfile modules, I started modifying the Python script ‘wq_blender.py’ to do the following:

  * Accept several parameters that the script will pass along to Blender’s command line tool. Currently the parameters include the input file, the format, and the number of frames to render, but the only format that currently works is PNG. I plan to expand the number of arguments allowed as needed.
  * Once all the jobs are submitted, the script notifies the user and provides a progress bar.
  * The output of each job is saved to a temporary directory in /tmp (EDIT: this is not necessarily true – the temp dir is created wherever the user has permissions, with /tmp being preferred).
  * After all the render jobs are complete, the script uses the subprocess module to call the ffmpeg command line tool and stitch all the temp files into a movie. Currently there are no options visible to the user, but in the future I plan to include various options for the final output.
  * Finally, the script deletes the temp directory.



This all only works on boxes that have Blender installed. I made an attempt to make it portable, but it will take more work than I thought. I also need to polish up the code quite a bit – I need to decide on which arguments I am going to allow; I need to create some functions to clean up the code; and I need to handle errors better (currently if the script fails, the temp directory does not get deleted).
