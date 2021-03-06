import subprocess
import shutil
from moviepy.editor import *
from directory_functions import *
from time import sleep
import datetime
from PIL import Image, ImageDraw, ImageFont
import threading
import random
from moviepy.config import get_setting

# This function is running in background, on another thread
def StartClip(config, clipsList):
    log = open(config["root_path"] + "logs/stream.log", "a+")

    print(len(clipsList))
    # If there are no rendered videos yet, we can't stream anything
    if len(clipsList) == 0:
        # Should print to log file
        log.write(str(datetime.datetime.now()).rsplit(".", 1)[0] + " There are no rendered clips yet.\n")
        sleep(30)
        log.close()
        return 1
    else:
        # This is the command that we are running
        # ffmpeg -re -i example-vid.mp4 -vcodec libx264 -preset ultrafast -maxrate 4M -minrate 0.5M -bufsize 2M -vprofile baseline -g 30 -acodec aac -tune zerolatency -pix_fmt yuv420p -vf pad=ceil(iw/2)*2:ceil(ih/2)*2 -strict -2 -f flv rtmp://localhost/show/

        t = threading.current_thread()
        while getattr(t, "loop", True):
            # Start streaming
            entry = random.choice(list(clipsList.keys()))
            # We loop through clipsList. We could manually add ready clips to clips folder as well.
            # For that, we would need a function that will insert that clip to clips.dat
            fileToPlay = config["clips_path"] + entry

            log.write(str(datetime.datetime.now()).rsplit(".", 1)[0] + " Starting clip: " + fileToPlay + "\n")
            log.flush()

            subprocess.run(
                (["ffmpeg", "-re", "-i", fileToPlay,
                  "-vcodec", "libx264", "-preset", "ultrafast", "-maxrate", config["streaming_maxrate"], "-minrate", config["streaming_minrate"],
                  "-bufsize", config["streaming_bufsize"], "-vprofile", "baseline", "-g", "30", "-acodec", "aac", "-tune", "zerolatency",
                  "-pix_fmt", "yuv420p", "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-strict", "-2", "-f", "flv",
                  "rtmp://localhost/show/"]))
            # ffmpeg will simply exit when done. Then we start a new stream
        log.write(str(datetime.datetime.now()).rsplit(".", 1)[0] + " Term signal received. Loop has stopped\n")

# Select mp3
def SelectMp3(mp3List, config):
    # Log
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    try:
        # Lowest number starts at first entry
        lowestRenderCount = list(mp3List.values())[0]
        for entry in mp3List:
            if mp3List[entry] <= lowestRenderCount:
                selectedMp3 = entry
                lowestRenderCount = mp3List[entry]
            elif mp3List[entry] == 0:
                # Value can't be lower than this, this is a new entry
                selectedMp3 = entry
                break

        if mp3List[selectedMp3] < config["clip_per_mp3"]:
            mainLog.close()
            return selectedMp3
        else:
            mainLog.close()
            return "END_RENDERING"
    except Exception as error:
        mainLog.write(now + "There was an error while selecting the mp3. Error message: " + str(error))
    mainLog.close()

# Resize image
def ResizeImage(image_path, config):
    # Log
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
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
        img_resized.save(config["root_path"] + "temp.jpg", "JPEG")
        #mainLog.write(now + " Image resized successfully.\n")
    except Exception as error:
        mainLog.write(now + " There was an error while resizing the image. image_path: " + image_path + "\n")
        mainLog.write("Error message: " + str(error) + "\n")

    mainLog.close()

def sortVidsList(clipLength, inputList, config, slideLen, selectedVids):
    # Log
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
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
    except Exception as error:
        mainLog.write(now + " There was an error while attempting to sort vidsList by render count. clipLength:" + str(clipLength) + "\n")
        mainLog.write("Error message: " + str(error) + "\n")

    mainLog.close()


def CreateTempClipsFromImages(theVids, fps, preset, threads, config):
    # Log
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    try:
        # Create temporary clips from the images
        i = 0
        # Purge the temp directory (delete and recreate)
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(config["root_path"] + "temp_img_clips")
        os.mkdir(config["root_path"] + "temp_img_clips")
        # We need this, because we can't override selectedVids, we need selectedVids to increment render count in the end
        actualPaths = theVids.copy()
        for img in theVids:
            if img.endswith(".jpg") or img.endswith(".png") or img.endswith(".jpeg") or img.endswith(
                    ".png") or img.endswith(".PNG"):
                # Create temporary resized image
                ResizeImage(img, config)
                myImgClip = ImageClip(config["root_path"] + "temp.jpg")
                # Set duration
                myImgClip.duration = int(config["image_slideshow_length"])
                newpath = config["root_path"] + "temp_img_clips/" + str(i) + ".mp4"
                # Start rendering
                myImgClip.write_videofile(newpath, fps, preset=preset, threads=threads, write_logfile=True)
                # Replace the path in the selectedVids array
                actualPaths[actualPaths.index(img)] = newpath
                # Delete temp img
                os.remove(config["root_path"] + "temp.jpg")
                i += 1
        mainLog.write(now + " All temporary mp4 files created successfully.\n")
        return actualPaths
    except Exception as error:
        mainLog.write(now + " There was an error while attempting to create the temporary mp4 files from the images.\n")
        mainLog.write("Error message: " + str(error) + "\n")

    mainLog.close()


def CreateText(config, selectedMp3):
    # Log
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    try:
        # This will be the text on the clip
        musicName = os.path.splitext(selectedMp3)[0]

        # Create empty image, get size from config
        image = Image.new('RGBA', (config["clip_width"], config["clip_height"]), (0, 0, 0, 0))

        # Create draw object
        draw = ImageDraw.Draw(image, "RGBA")
        # Set font. Second parameter is font size
        font = ImageFont.truetype(config["root_path"] + "font.ttf", int(config["font_size"]))
        # Write on transparent image
        red = int(config["font_color_rgba"].split(",")[0])
        green = int(config["font_color_rgba"].split(",")[1])
        blue = int(config["font_color_rgba"].split(",")[2])
        alpha = int(config["font_color_rgba"].split(",")[3])
        draw.text((int(config["clip_width"] * 0.05), int(config["clip_height"] * 0.85)), musicName,
                  fill=(red, green, blue, alpha), font=font)
        # If logo exists, insert logo
        if os.path.isfile(config["root_path"] + "logo.png"):
            logo = Image.open(config["root_path"] + "logo.png")
            logo = logo.resize((80, 80))
            image.paste(logo, (int(config["clip_width"] * 0.92), int(config["clip_height"] * 0.03)))

        # Save image
        image.save(config["root_path"] + "text_layer.png", "PNG")
        mainLog.write(now + " Text layer created successfully.\n")
    except Exception as error:
        mainLog.write(now + " There was an error while creating the text layer.\n")
        mainLog.write("Error message: " + str(error) + "\n")

    mainLog.close()
    return 0


def FinalClip(paths, mp3File, clipLength, config):
    # Log
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    try:
        # Create the final clip object
        # We create a clip object from every path
        clips = []
        for i in range(0, len(paths)):
            # Original resolution
            origRes = VideoFileClip(paths[i]).size
            # This needs to be modified by aspect ration ratio, one extra multiplication
            widthRatio = config["clip_width"] / origRes[0]
            heightRatio = config["clip_height"] / origRes[1]
            # Aspect difference
            aspect_difference = ( float((origRes[0])/float(origRes[1])) / (float(config["clip_width"])/float(config["clip_height"])) )

            target_width = config["clip_width"]
            target_height = config["clip_height"]
            # Wide aspect ratio
            if aspect_difference > 1.0:
                target_width = int(widthRatio * origRes[0])
                target_height = int(heightRatio * origRes[1] / aspect_difference)
            # Standing aspect ratio
            if aspect_difference < 1.0:
                target_width = int(widthRatio * origRes[0] * aspect_difference)
                target_height = int(heightRatio * origRes[1])
            clips.append(VideoFileClip(paths[i], target_resolution=(target_height, target_width)))

        # Concatenating video clips (that are already clip objects)
        # Without method="compose", result mp4 wouldn't play, because of different screen resolutions
        clipWithoutAudio = concatenate_videoclips(clips, method="compose")
        text = ImageClip(config["root_path"] + "text_layer.png")
        clipWithText = CompositeVideoClip([clipWithoutAudio, text])
        clipWithText.duration = clipLength

        finalClip = clipWithText.set_audio(AudioFileClip(config["mp3_path"] + mp3File))
        mainLog.write(now + " Final clip created\n")
        mainLog.close()
        return finalClip
    except Exception as error:
        mainLog.write(now + " There was an error during the creation of the final clip object.\n")
        mainLog.write("Error message: " + str(error) + "\n")
    mainLog.close()

# Write the final MP4
def WriteClip(theClip, fps, preset, threads, config):
    # Log
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
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
        mainLog.close()
        return True
    except Exception as error:
        mainLog.write(now + " There was an error while rendering the final MP4 file.\n")
        mainLog.write("Error message: " + str(error) + "\n")


# Increment render counts for all elements, but only after rendering was successful
def SaveChanges(selectedVids, selectedMp3, vidsList, mp3List, clipsList, config):
    # Log
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    try:
        for i in range(0, len(selectedVids)):
            vidsList[selectedVids[i].rsplit("/", 1)[1]] = vidsList[selectedVids[i].rsplit("/", 1)[1]] + 1
            #vidsList[element] = vidsList[element] + 1
        mp3List[selectedMp3] = mp3List[selectedMp3] + 1
        # Insert the new mp4 to the clips dictionary
        clipsList[str(config["next_clip_to_create"]) + ".mp4"] = selectedMp3
        # Increment video counter for the ready 'clips' folder
        config["next_clip_to_create"] = config["next_clip_to_create"] + 1
        # Updating the config file
        assert WriteConfig(config)
        # Updating the list files
        assert WriteLists(config, vidsList, mp3List, clipsList)
        mainLog.write(now + " Changes successfully saved.\n")
        mainLog.close()
    except Exception as error:
        mainLog.write(now + " Couldn't write changes to dat files or the config file. Maybe one of the files is being edited by StartClip.\n")
        mainLog.write("Error message: " + str(error) + "\n")
        print(" ERROR: " + str(error))




# Create a new clip, using 1 mp3 file and multiple pictures and videos
def CreateClip(config, vidsList, mp3List, clipsList):
    # Log
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
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
    os.environ["IMAGEMAGICK_BINARY"] = config["magick_path"]
    # Set FPS
    fps = 25
    # Can be ultrafast / superfast / veryfast / faster / fast / medium / slow / slower / veryslow /placebo
    # According to write_videofile docs, this will affect file size, but not quality (faster rendering ~ larger size)
    preset = config["preset"]
    # Number of threads to use (when rendering final video)
    threads = config["render_threads"]


    # Select mp3
    selectedMp3 = SelectMp3(mp3List, config)
    if selectedMp3 == "END_RENDERING":
        # End the rendering process, because all mp3 files are processed
        mainLog.write(now + " All mp3 files reached desired render count\n")
        mainLog.close()
        # Here there could be a script, that is transfering clips to the other server, then shuts down the machine.
        # We will wait 5 minutes, we don't want to fill up the log files.
        sleep(300)
        return 2
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

    # Create text img
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]
    CreateText(config, selectedMp3)

    # Create the final clip object
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]
    mainLog.write(now + " Creating the final clip object\n")
    mainLog.flush()
    finalClip = FinalClip(actualPaths, selectedMp3, mp3Duration, config)


    # Write the mp4 file
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]
    mainLog.write(now + " Rendering video to mp4...\n")
    mainLog.flush()
    isRenderSuccessful = WriteClip(finalClip, fps, preset, threads, config)

    # Save changes to files
    if isRenderSuccessful:
        SaveChanges(selectedVids, selectedMp3, vidsList, mp3List, clipsList, config)

    mainLog.close()

    print("config: ", config)
    print("vidsList: ", vidsList)
