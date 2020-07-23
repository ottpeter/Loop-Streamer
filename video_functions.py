import subprocess
import os
import shutil
from moviepy.editor import *
from directory_functions import *

def StartClip(config, clipsList):
    # Check if previous clip is still running
    # We assume that clip finished by duration
    # There should be another method beside that, because of possible lag

    print(len(clipsList))
    # If there are no rendered videos yet, we can't stream anything
    if len(clipsList) == 0:
        print("There are no rendered clips yet")
        return 1

    # ffmpeg -re -i example-vid.mp4 -vcodec libx264 -vprofile baseline -g 30 -acodec aac -strict -2 -f flv rtmp://localhost/show/
    #subprocess.run(["ffmpeg", "-version"])
    # We don't know if every parameter is an element in the array, or every word
    subprocess.run((["ffmpeg", "-re", "-i", config["clips_path"] + str(config["next_clip_to_play"]) + ".mp4", "-vcodec", "libx264", "-vprofile", "baseline", "-g", "30", "-acodec", "aac", "-strict", "-2", "-f", "flv", "rtmp://localhost/show/"]))
    # Remembering PID would be really good
    print("Would start clip: ", str(config["next_clip_to_play"]) + ".mp4")

# Create a new clip, using 1 mp3 file and multiple pictures and videos
def CreateClip(config, vidsList, mp3List, clipsList):
    # If render is successful, we increment render count for all participating elements
    isRenderSuccessful = False
    # We need mp3 duration for the selection of vids
    mp3Duration = 0
    # All the vids & pictures with specific slideshow length
    allVidsDuration = 0.0
    # Only 1 selected mp3
    selectedMp3 = ""
    # Array of selected pictures & videos
    selectedVids = []
    # Slide show frame length
    slideLen = config["image_slideshow_length"]
    # Set environment variable
    os.environ["IMAGEIO_FFMPEG_EXE"] = config["ffmpeg_path"]
    # Set FPS
    fps = 25
    # Can be ultrafast / superfast / veryfast / faster / fast / medium / slow / slower / veryslow /placebo
    # According to write_videofile docs, this will affect file size, but not quality (faster rendering ~ larger size)
    preset = config["preset"]
    # Number of threads to use (when rendering final video)
    threads = config["threads"]

    # Lowest number starts at first entry
    lowestRenderCount = list(mp3List.values())[0]
    for entry in mp3List:
        if mp3List[entry] < lowestRenderCount:
            selectedMp3 = entry
        elif mp3List[entry] == 0:
            # Value can't be lower than this, this is a new entry
            selectedMp3 = entry
            break
    print("Selected mp3: ", selectedMp3)

    mp3Duration = ((AudioFileClip(config["mp3_path"] + selectedMp3)).duration)
    print("mp3 duration: ", mp3Duration)

    # Sort vidsList by render count
    vidsSortedArray = sorted(vidsList.items(), key=lambda x: x[1], reverse=False)
    # print("[0][0]: ", vidsSortedArray[0][0])
    # print("[0][1]: ", vidsSortedArray[0][1])
    index = 0
    while mp3Duration > allVidsDuration:
        print("fill the clip")

        # Set the complete file path
        print("index", index)
        currentFile = config["vids_path"] + vidsSortedArray[index][0]
        # Supported image extension: .jpg, .jpeg, .png, .JPG, .PNG
        if currentFile.endswith(".jpg") or currentFile.endswith(".png") or currentFile.endswith(".jpeg") or currentFile.endswith(".png") or currentFile.endswith(".PNG"):
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
        print(currentFile + " - ", currentDuration)

        if (index < len(vidsSortedArray)-1):
            index += 1
        else:
            index = 0
    # After this, we should have an array of the elements that we are going to use
    print("Total duration: ", allVidsDuration)

    # Should create function SelectMp3(), SelectVids()


    # Create temporary clips from the images
    i = 0
    # Purge the temp directory (delete and recreate)
    shutil.rmtree("temp_img_clips")
    os.mkdir("./temp_img_clips")
    # We need this, because we can't override selectedVids, we need selectedVids to increment render count in the end
    actualPaths = selectedVids.copy()
    for img in selectedVids:
        if img.endswith(".jpg") or img.endswith(".png") or img.endswith(".jpeg") or img.endswith(".png") or img.endswith(".PNG"):
            print("img: ", img)
            myImgClip = ImageClip(img)
            # Set duration
            myImgClip.duration = int(slideLen)
            newpath = "./temp_img_clips/" + str(i) + ".mp4"
            # Start rendering
            myImgClip.write_videofile(newpath, fps, preset="fast")
            #myImgClip.write_videofile("./temp_img_clips/" + str(i) + ".mp4", fps, preset="fast")
            # Replace the path in the selectedVids array
            actualPaths[actualPaths.index(img)] = newpath
            i += 1

    # Maybe we should rethink this.
    # Surely we need to convert images
    # We also surely need to creat clips[] array
    # That should be inside a function with clipsWithoutAudio, finalClip,
    # The previous things should be another function
    # increment render cound does not need to be in a function

    # Create the final clip object
    # We create a clip object from every path
    # We couold have done this when processing images
    clips = []
    for i in range(0, len(actualPaths)):
        clips.append(VideoFileClip(actualPaths[i], target_resolution=(1080, 1920)))


    # Concatenating video clips (that are already clip objects)
    # Without method="compose", result mp4 wouldn't play, because of different screen resolutions
    clipWithoutAudio = concatenate_videoclips(clips, method="compose")
    # This will cut the end. Other solution would be to decrease slideLen, for example 10 sec -> 9.2 sec, so it exacty fills the mp3
    clipWithoutAudio.duration = mp3Duration
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
    # print("selectedmp3: ", selectedMp3)
    finalClip = clipWithoutAudio.set_audio(AudioFileClip(config["mp3_path"] + selectedMp3))
    # print("duration: ", finalVideoClip.duration)
    # This is the line that will actually create the mp4 file
    finalClip.write_videofile(
        config["clips_path"] + str(config["next_clip_to_create"]) + ".mp4",
        fps=fps,
        preset="medium",
        write_logfile=True,
        threads=2)
    # We could add audio by parameter

    # File will probably exist if it's corrupted as well. Better method would be logs
    # It's seems when no error, last thing in log file will be kb/s rate
    isRenderSuccessful = os.path.isfile(config["clips_path"] + str(config["next_clip_to_create"]) + ".mp4")
    #isRenderSuccessful = True


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




