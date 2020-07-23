import os

def RemoveLocks():
    if os.path.isfile("config.lock"):
        os.remove("config.lock")
    if os.path.isfile("vids.lock"):
        os.remove("vids.lock")
    if os.path.isfile("mp3.lock"):
        os.remove("mp3.lock")
    if os.path.isfile("clips.lock"):
        os.remove("clips.lock")

RemoveLocks()