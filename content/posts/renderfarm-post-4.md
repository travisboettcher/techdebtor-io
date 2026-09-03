---
title: "[RenderFarm] Post 4"
date: 2013-02-22T10:27:19+00:00
tags: []
summary: "This past week has been rather productive for the project. I have accomplished the following: I cleaned up the code somewhat (although it still looks like a 5…"
draft: true
archive_url: "https://web.archive.org/web/20131223053053/http://futurecyb.org/?p=73"
archive_source: "futurecyb.org"
---

This past week has been rather productive for the project. I have accomplished the following:

  * I cleaned up the code somewhat (although it still looks like a 5 year old organized it);
  * the progress bar now includes the percentage and elapsed time of the rendering process;
  * I implemented the argparse module to add a few options to wq_blender;
  * I cleaned up the output using the `-loglevel panic` option for ffmpeg. It will still ask you if you want to overwrite a file if it is already there, but that might be a good feature to have;
  * and with some help, now the script works with WorkQueue to distribute the work to a cluster.



I still have to implement the logging module so that we have some form of debugging – several options I added with the argparse module are commented out currently because they rely on having a way to debug. One of the other options I commented out specifies a temp directory. I don’t know if this is necessary - `tempfile.mkdtemp()` creates a temp directory wherever it can, starting with `/temp`. In the end the temp directory and all the files get deleted so that the user never sees them. Therefore, I’m inclined to blackbox the entire temp file/directory thing and let the script handle it.

One last thing: creating a progress bar from scratch isn’t too difficult, but I sure learned some fun things about formatting text and `sys.stdout.write()`!
