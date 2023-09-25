tools-watcher
================

Overview
----------------

This is just a simple web application that allows me to compare the current webcam
video with previously saved refernce images, in an effort to identify missing
tools hanging on a wall in my shop.

The initial functional software was developed in about a day with 90% of the
code being generated/manipuated via ChatGPT prompts.

I'm not a Node, React, Flask, or OpenCV developer,
so it's very likely the code could use some craft work, but it works.


A Word on Container Tech
----------------

I had ChatGPT help solve a problem I often hit, I want the software to build/run regardless
of the container software installed on the host. Ideally it supports each of these permutations:

* Rootless podman
* Rootless docker
* Rootful podman (using sudo as necessary)
* Rootful docker (using sudo as necessary)

To this ends, the build/run scripts use a `contaier.sh` to identify/target the appropriate
contiaer software.

One caveat: I have not tested rootless actions, and I suspect the mount related arguments
I am using might break in that scenario.


Usage
----------------

Build the image:L

    ./build.sh

Run:

    ./run.sh

... and the webserver will be up at:

    http://127.0.0.1:5000/

Develop:

    ./run-dev.sh /bin/bash

... where the latter mounts the source code in a container running the node/python environment,
so we can use tools like `npm` action to affect source files suchs as `package.json`.





