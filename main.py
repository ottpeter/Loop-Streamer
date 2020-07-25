#!/usr/bin/env python 

from time import sleep
import signal
import threading
import datetime
import sys
from directory_functions import *
from video_functions import *
from remove_locks import RemoveLocks


# Dictionary that contains configuration parameters
config = {
    "vids_path": "",
    "mp3_path": "",
    "clips_path": "",
    "empty_time": 0,
    "next_clip_to_play": 0,
    "next_clip_to_create": 0,
    # How many seconds an image should be shown in slideshow (this won't affect already rendered clips)
    "image_slideshow_length": 10,
}

# Dictionary that contains the file names of videos & pictures
# Number indicates how many times it was rendered into clip
vids = {

}

# Dictionary that contains the file names of mp3s
# Number indicates how many times it was rendered into clip
mp3 = {

}

# Dictionary that contains the file names of clips, they will be numbered and with extension .mp4
# Can contain name of the music that it is containing. 1 clip is made of 1 mp3 file
clips = {

}

isRunning = True

# This function handles SIGTERM
def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0)
    sys.exit(0)


def Init():
    print("Welcome!")
    # Read the files where we keep already scanned vids&mp3s, put them in arrays
    # LOG
    ReadConfig(config)
    ReadLists(config, vids, mp3, clips)
    CheckNewFiles(config, vids, mp3)
    # First we start serving already existing clips with ffmpeg
    # We will start StartClip in a background process. It will loop existing videos
    backgroundThread.start()
    # Testing only
    # ResizeImage("/home/user/Downloads/vids/assorted-books-on-green-wooden-chair-3494936.jpg", config)


def Exit():
    RemoveLocks()
    backgroundThread.loop = False
    print("Goodbye")
    # We should print to log



def Core():
    # Log
    mainLog = open("logs/main.log", "a")
    global backgroundThread
    # Current time, without microseconds
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]
    start_rendering = datetime.datetime.strptime(config["render_start"], "%H:%M")
    stop_rendering = datetime.datetime.strptime(config["render_stop"], "%H:%M")
    # It will be 1900 Jan 1 and given time
    mainLog.write(now + " Entering Core loop...\n")
    if backgroundThread.is_alive():
        mainLog.write(now + " StartClip loop is running\n")
        mainLog.flush()
    else:
        mainLog.write(now + " StartClip loop stopped unexpectedly. Restarting StartClip...\n")
        backgroundThread = None
        backgroundThread = threading.Thread(target=StartClip, args=[config, clips])
        backgroundThread.start()
        mainLog.flush()
        if backgroundThread.is_alive():
            now = str(datetime.datetime.now()).rsplit(".", 1)[0]
            mainLog.write(now + " StartClip loop is now running!\n")
        else:
            mainLog.write(now + " Couldn't restart StartClip.\n")
    mainLog.flush()

    mainLog.write(now + " Checking new files...\n")
    CheckNewFiles(config, vids, mp3)
    if config["rendering"] == "on" \
            and datetime.datetime.now().time() > start_rendering.time() \
            and datetime.datetime.now().time() < stop_rendering.time():
        mainLog.write(now + " Creating a new clip...\n")
        mainLog.flush()
        CreateClip(config, vids, mp3, clips)
    else:
        # Wait 5 minutes
        sleep(300)
    mainLog.close()
    sleep(1)


try:
    # Program is running
    # Create background thread object. Init() will start background thread
    backgroundThread = threading.Thread(target=StartClip, args=[config, clips])
    Init()
    # Infinite loop until interupt
    while isRunning:
        Core()
        if sys.argv[0] == "handle_signal":
            signal.signal(signal.SIGTERM, sigterm_handler)
            isRunning = False

finally:
    # Program exiting
    Exit()
