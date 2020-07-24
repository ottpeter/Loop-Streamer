import subprocess
import os
import shutil
from moviepy.editor import *
from directory_functions import *
from time import sleep
from time import time
import datetime
from  PIL import Image

# This function is running in background, on another thread
def StartClip(config, clipsList):
    log = open("logs/stream.log", "a")

    print(len(clipsList))
    # If there are no rendered videos yet, we can't stream anything
    if len(clipsList) == 0:
        # Should print to log file
        print("There are no rendered clips yet")
        return 1
    else:
        # This is the command that we are running
        # ffmpeg -re -i example-vid.mp4 -vcodec libx264from subprocess import check_output -vprofile baseline -g 30 -acodec aac -strict -2 -f flv rtmp://localhost/show/

        while True:
            # Start streaming

            #subprocess.run((["ffmpeg", "-re", "-i", config["clips_path"] + str(config["next_clip_to_play"]) + ".mp4",
            #                "-vcodec", "libx264", "-vprofile", "baseline", "-g", "30", "-acodec", "aac", "-strict", "-2", "-f", "flv", "rtmp://localhost/show/"]))
            ts = str(time())
            ts = ts.rsplit(".", 1)[0]
            args = ["ffmpeg", "-re", "-i", config["clips_path"] + str(config["next_clip_to_play"]) + ".mp4", "-vcodec", "libx264",
             "-vprofile", "baseline", "-g", "30", "-acodec", "aac", "-strict", "-2", "-f", "flv",
             "rtmp://localhost/show/"]
            with open("logs/stream_std/" + ts + ".log", "wb") as out, open("logs/stream_err/" + ts + ".log", "wb") as err:
                subprocess.Popen(args=args, bufsize=0, stdout=out, stderr=err)
            # Remembering PID would be really good
            log.write(str(datetime.datetime.now()) + " Starting clip: " + str(config["next_clip_to_play"]) + ".mp4\n")
            log.flush()
            # ffmpeg will simply exit when done. Then we start a new stream
            # Increment next_clip_to_play
            if config["next_clip_to_play"] + 1 == config["next_clip_to_create"]:
                # We can't play mp4 that is being created
                config["next_clip_to_play"] = 0
            else:
                config["next_clip_to_play"] += 1
            # Might or might not need this
            sleep(1)
        log.close()


# Select mp3
def SelectMp3(mp3List, config):
    # Log
    mainLog = open("logs/main.log", "a")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    try:
        # Lowest number starts at first entry
        lowestRenderCount = list(mp3List.values())[0]
        for entry in mp3List:
            if mp3List[entry] <= lowestRenderCount:
                selectedMp3 = entry
            elif mp3List[entry] == 0:
                # Value can't be lower than this, this is a new entry
                selectedMp3 = entry
                break

        mainLog.close()
        return selectedMp3
    except:
        mainLog.write(now + "There was an error while selecting the mp3.")
    mainLog.close()

# Resize image
def ResizeImage(image_path, config):
    # Log
    mainLog = open("logs/main.log", "a")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    try:
        img = Image.open(image_path)
        width, height = img.size
        res_ratio = (width / height) / (config["clip_width"] / config["clip_height"])
        print(res_ratio)

        # adjust to left-right edge
        if width / height > config["clip_width"] / config["clip_height"]:
            print("wide")
            size = config["clip_width"], int(config["clip_height"] / res_ratio)
        # adjust to top-bottom
        else:
            print("standing")
            size = int(config["clip_width"] * res_ratio), config["clip_height"]

        img_resized = img.resize(size, Image.ANTIALIAS)
        img_resized.save("temp.jpg", "JPEG")
        # We will comment this out
        mainLog.write(now + " Image resized successfully.\n")
    except:
        mainLog.write(now + " There was an error while resizing the image. image_path: " + image_path + "\n")

    mainLog.close()

def sortVidsList(clipLength, inputList, config, slideLen, selectedVids):
    # Log
    mainLog = open("logs/main.log", "a")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    allVidsDuration = 0.0
    # Attempting to sort vidsList by render count
    try:
        vidsSortedArray = sorted(inputList.items(), key=lambda x: x[1], reverse=False)
        # print("[0][0]: ", vidsSortedArray[0][0])
        # print("[0][1]: ", vidsSortedArray[0][1])
        index = 0
        while clipLength > allVidsDuration:
            # Set the complete file path
            currentFile = config["vids_path"] + vidsSortedArray[index][0]
            # Supported image extension: .jpg, .jpeg, .png, .JPG, .PNG
            if currentFile.endswith(".jpg") or currentFile.endswith(".png") or currentFile.endswith(
                    ".jpeg") or currentFile.endswith(".png") or currentFile.endswith(".PNG"):
                currentDuration = slideLen
            else:
                # Get the duration of the video file
                currentDuration = VideoFileClip(currentFile).duration
                if currentDuration == 0.04:
                    # most likely this is an image that we failed to recognize as image (1 second is 25 frame => 1/25=0.04)
                    print("CURRENT DURATION IS 0.04")
                    currentDuration = slideLen
            # Append the video to the selected videos list, and add duration to all duration
            selectedVids.append(currentFile)
            allVidsDuration += float(currentDuration)
            # Test
            # print(currentFile + " - ", currentDuration)

            if (index < len(vidsSortedArray) - 1):
                index += 1
            else:
                index = 0
    except:
        mainLog.write(now + " There was an error while attempting to sort vidsList by render count.\n")

    mainLog.close()


def CreateTempClipsFromImages(theVids, fps, preset, threads, config):
    # Log
    mainLog = open("logs/main.log", "a")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]


    try:
        # Create temporary clips from the images
        i = 0
        # Purge the temp directory (delete and recreate)
        shutil.rmtree("temp_img_clips")
        os.mkdir("./temp_img_clips")
        # We need this, because we can't override selectedVids, we need selectedVids to increment render count in the end
        actualPaths = theVids.copy()
        for img in theVids:
            if img.endswith(".jpg") or img.endswith(".png") or img.endswith(".jpeg") or img.endswith(
                    ".png") or img.endswith(".PNG"):
                # Create temporary resized image
                ResizeImage(img, config)
                myImgClip = ImageClip("temp.jpg")
                # Set duration
                myImgClip.duration = int(config["image_slideshow_length"])
                newpath = "./temp_img_clips/" + str(i) + ".mp4"
                # Start rendering
                myImgClip.write_videofile(newpath, fps, preset=preset, threads=threads, write_logfile=True)
                # Replace the path in the selectedVids array
                actualPaths[actualPaths.index(img)] = newpath
                # Delete temp img
                os.remove("temp.jpg")
                i += 1
        mainLog.write(now + " All temporary mp4 files created successfully.\n")
        return actualPaths
    except:
        mainLog.write(now + " There was an error while attempting to create the temporary mp4 files from the images.\n")

    mainLog.close()


def CreateText():
    print("nothing")
    '''
    # Create text
    # We could get mp3 name from meta tag (if exists)
    text = TextClip(
        "example",
        size="22",
        color="black",
        bg_color="transparent",
        fontsize=32,
        font="Courier",
        align="bottom")
    clipWithoutAudio = CompositeVideoClip(clipWithoutAudio, text)
    '''


def FinalClip(paths, mp3File, clipLength, config):
    # Log
    mainLog = open("logs/main.log", "a")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    try:
        # Create the final clip object
        # We create a clip object from every path
        clips = []
        for i in range(0, len(paths)):
            clips.append(VideoFileClip(paths[i], target_resolution=(1080, 1920)))

        # Concatenating video clips (that are already clip objects)
        # Without method="compose", result mp4 wouldn't play, because of different screen resolutions
        clipWithoutAudio = concatenate_videoclips(clips, method="compose")
        clipWithoutAudio.duration = clipLength

        finalClip = clipWithoutAudio.set_audio(AudioFileClip(config["mp3_path"] + mp3File))
        mainLog.write(now + " Final clip created\n")
        mainLog.close()
        return finalClip
    except:
        mainLog.write(now + " There was an error during the creation of the final clip object.\n")
    mainLog.close()

# Write the final MP4
def WriteClip(theClip, fps, preset, threads, config):
    # Log
    mainLog = open("logs/main.log", "a")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    try:
        theClip.write_videofile(
            config["clips_path"] + str(config["next_clip_to_create"]) + ".mp4",
            fps=fps,
            preset="medium",
            write_logfile=True,
            threads=2)
        # We could add audio by parameter
        mainLog.write(now + " Rendering was successful. Clip name: " + str(config["next_clip_to_create"]) + ".mp4\n")
    except:
        mainLog.write(now + " There was an error while rendering the final MP4 file.")
    mainLog.close()


# Create a new clip, using 1 mp3 file and multiple pictures and videos
def CreateClip(config, vidsList, mp3List, clipsList):
    # Log
    mainLog = open("logs/main.log", "a")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    # If render is successful, we increment render count for all participating elements
    isRenderSuccessful = False
    # We need mp3 duration for the selection of vids
    mp3Duration = 0
    # Only 1 selected mp3
    selectedMp3 = ""
    # Array of selected pictures & videos
    selectedVids = []
    # Actual paths (altered path, temp folder)
    actualPaths = []
    # Slide show frame length
    #slideLen = config["image_slideshow_length"]
    # Set environment variable
    os.environ["IMAGEIO_FFMPEG_EXE"] = config["ffmpeg_path"]
    # Set FPS
    fps = 25
    # Can be ultrafast / superfast / veryfast / faster / fast / medium / slow / slower / veryslow /placebo
    # According to write_videofile docs, this will affect file size, but not quality (faster rendering ~ larger size)
    preset = config["preset"]
    # Number of threads to use (when rendering final video)
    threads = config["render_threads"]


    # Select mp3
    selectedMp3 = SelectMp3(mp3List, config)
    mp3Duration = ((AudioFileClip(config["mp3_path"] + selectedMp3)).duration)
    mainLog.write(now + " Selected mp3: " + selectedMp3 + ", duration: " + str(mp3Duration) + "\n")
    mainLog.flush()
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    # Select videos to fill the clip
    mainLog.write(now + " Selecting videos to fill the clip...\n")
    sortVidsList(mp3Duration, vidsList, config, config["image_slideshow_length"], selectedVids)

    # Create temporary mp4 files from images
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]
    mainLog.write(now + " Converting images to mp4 files...\n")
    mainLog.flush()
    actualPaths = CreateTempClipsFromImages(selectedVids, fps, preset, threads, config)

    # Create text clip
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]
    CreateText()

    # Create the final clip object
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]
    mainLog.write(now + " Creating the final clip object\n")
    finalClip = FinalClip(actualPaths, selectedMp3, mp3Duration, config)
    mainLog.flush()

    # Write the mp4 file
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]
    mainLog.write(now + " Writing mp4...\n")
    WriteClip(finalClip, fps, preset, threads, config)
    mainLog.flush()

    # Save changes to files

    # Increment render counts for all elements, but only after rendering was successful
    if isRenderSuccessful:
        for i in range(0, len(selectedVids)):
            vidsList[selectedVids[i].rsplit("/", 1)[1]] = vidsList[selectedVids[i].rsplit("/", 1)[1]] + 1
            #vidsList[element] = vidsList[element] + 1
        mp3List[selectedMp3] = mp3List[selectedMp3] + 1
        # Insert the new mp4 to the clips dictionary
        clipsList[str(config["next_clip_to_create"]) + ".mp4"] = selectedMp3
        # Increment video counter for the ready 'clips' folder
        config["next_clip_to_create"] = config["next_clip_to_create"] + 1
        # Updating the config file
        WriteConfig(config)
        # Updating the list files
        WriteLists(config, vidsList, mp3List, clipsList)
