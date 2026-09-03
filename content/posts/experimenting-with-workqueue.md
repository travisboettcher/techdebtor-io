---
title: "Experimenting with WorkQueue"
date: 2013-02-07T22:05:43+00:00
tags: []
summary: "This week for the [RenderFarm] project I experimented with WorkQueue and Python. After thoroughly examining some examples I found online (here and here) I went…"
draft: true
archive_url: "https://web.archive.org/web/20160731092114/http://futurecyb.org/?p=60"
archive_source: "futurecyb.org"
---

This week for the [RenderFarm] project I experimented with WorkQueue and Python. After thoroughly examining some examples I found online ([here](https://www3.nd.edu/~ccl/software/manuals/work_queue_example.py) and [here](https://bitbucket.org/badi/python-workqueue/raw/ab639bba0c37d51f4be925a0c5ef016a3ddcb83e/workqueue_example.py)) I went ahead and tried my hand at a script of my own. The following uses the command-line ‘convert’ to convert images from one file format to .PNG, and is heavily modeled after the examples.

> 
>     #!/usr/bin/env python2
>     
>     from work_queue import *
>     import sys
>     import os
>     
>     port = WORK_QUEUE_DEFAULT_PORT
>     
>     if len(sys.argv) < 2:
>         print "wq_convert <file1> [file2] [file3] ..."
>         print "Each file given on the command line will be converted to .PNG"
>         sys.exit(1)
>     
>     try:
>         wq = WorkQueue(port)
>     except:
>         print "Instantiation of Work Queue failed!"
>         sys.exit(1)
>     
>     print "listening on port %d..." % wq.port
>     
>     for i in range(1, len(sys.argv)):
>         infile = "%s" % sys.argv[i]
>         outfile = os.path.splitext("%s" % sys.argv[i])[0] + ".PNG"
>         command = "./convert %s %s" % (infile, outfile)
>     
>         task = Task(command)
>     
>         task.specify_file("/data/software/all-2013Q1/bin/convert", "convert", WORK_QUEUE_INPUT, cache=True)
>         task.specify_input_file(infile, infile)
>         task.specify_output_file(outfile, outfile)
>         taskid = wq.submit(task)
>     
>         print "submitted task (id# %d): %s" % (taskid, task.command)
>     
>     print "waiting for tasks to complete..."
>     
>     while not wq.empty():
>         task = wq.wait(1)
>         if task:
>             print(task.command, task.result)
>     
>     print "all tasks complete"
>     
>     sys.exit(0)

Another I did is basically the same except for the command. Instead of converting the file into another file format, I made a thumbnail with this:

> 
>     file = os.path.splitext(sys.argv[i])
>     infile = "%s" % sys.argv[i]
>     outfile = file[0] + "_thumb" + file[1]
>     command = "./convert -size 120x120 %s -resize 120x120 %s" % (infile, outfile)

Most of this worked well, except I kept getting an error that it failed to retrieve the output file. Sometimes it would work, but most often it would not.
