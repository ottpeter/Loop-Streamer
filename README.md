# Loop-Streamer
Streaming videos &amp; mp3 from 2 folder, sends it to nginx that is doing HLS.

The videos are edited with the moviepy python library. Moviepy is using ffmpeg.

Python has to be version 3.
~/.bashrc needs to contain line "alias python=python3.5"

moviepy needs to be installed.
It can be installed with pip, first need to have pip:
$ apt install python3-pip

Then moviepy can be installed with:
$ pip3 install moviepy


Timezone on the server needs to be set, see [this manual](https://linuxize.com/post/how-to-set-or-change-timezone-on-debian-10/).

Need to download nginx with RTMP module, and create a service for it (the original nginx service needs to be deactivated)

## Install with Docker

1) Copy 'home' folder to desired location(Example: `cp -R home/* /home/`    You can copy it to any location.)
2) Create _config.conf_, use config.conf.save as a template. Important: ___root_path___, ___clips_path___, ___mp3_path___, ___vids_path___.
3) _start.sh_ needs to point to the home folder
4) Build docker image: `docker build -t app` .
5) Run docker image: `docker run -v /home:/home app` (on host machine, _/home_ will be connected to docker _/home_)