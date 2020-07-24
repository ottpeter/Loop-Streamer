from time import sleep
import signal
import threading
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


# This function handles SIGTERM
def sigterm_handler(_signo, _stack_frame):
    # Raises SystemExit(0)
    sys.exit(0)


if sys.argv[0] == "handle_signal":
    signal.signal(signal.SIGTERM, sigterm_handler)


def Init():
    print("Welcome!")
    # Read the files where we keep already scanned vids&mp3s, put them in arrays
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
    print("Goodbye")



def Core():
    mainLog = open("logs/main.log", "a")
    # Current time, without microseconds
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]
    mainLog.write(now + " Entering Core...\n")
    if backgroundThread.is_alive():
        mainLog.write(now + " StartClip loop is running\n")
        mainLog.flush()
    else:
        mainLog.write(now + " StartClip loop stopped unexpectedly. Restarting StartClip...\n")
        newThread = threading.Thread(target=StartClip, args=[config, clips])
        newThread.start()
        mainLog.flush()
        if (newThread.is_alive()):
            now = str(datetime.datetime.now()).rsplit(".", 1)[0]
            mainLog.write(now + "StartClip loop is now running!\n")
        else:
            mainLog.write("Couldn't restart StartClip.\n")
    mainLog.flush()

    mainLog.write(now + " Checking new files...\n")
    CheckNewFiles(config, vids, mp3)
    mainLog.write(now + " Creating a new clip...\n")
    CreateClip(config, vids, mp3, clips)
    mainLog.close()
    sleep(1)


try:
    # Program is running
    # Create background thread object. Init() will start background thread
    backgroundThread = threading.Thread(target=StartClip, args=[config, clips])
    Init()
    # Infinite loop until interupt
    while True:
        Core()
finally:
    # Program exiting
    Exit()
