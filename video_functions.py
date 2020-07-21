import subprocess
import os
import shutil
from moviepy.editor import *

def StartClip(config, clipsList):
    # Check if previous clip is still running
    # We assume that clip finished by duration
    # There should be another method beside that, because of possible lag

    print(len(clipsList))
    # If there are no rendered videos yet, we can't stream anything
    if len(clipsList) == 0:
        print("There are no rendered clips yet")
        return 0

    subprocess.run(["ffmpeg", "-version"])


def CreateClip(config, vidsList, mp3List, clipsList):
    # Video editing
    # Possibly not with ffmpeg
    subprocess.run(["echo", "\n\n... video editing ..."])
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

    # Select an mp3 with lowest render count. #Initial value is max int.
    #lowestRenderCount = 2147483646
    # Lowest number starts at first entry
    lowestRenderCount = list(mp3List.values())[0]
    for entry in mp3List:
        if mp3List[entry] < lowestRenderCount:
            selectedMp3 = entry
        if mp3List[entry] == 0:
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

        if (index < len(vidsSortedArray)):
            index += 1
        else:
            index = 0
    # After this, we should have an array of the elements that we are going to use
    print("Total duration: ", allVidsDuration)

    # Create temporary clips from the images
    i = 0
    shutil.rmtree("temp_img_clips")
    os.mkdir("./temp_img_clips")
    for img in selectedVids:
        if img.endswith(".jpg") or img.endswith(".png") or img.endswith(".jpeg") or img.endswith(".png") or img.endswith(".PNG"):
            print("img: ", img)
            myImgClip = ImageClip(img)
            myImgClip.duration = 10
            print(myImgClip.duration)
            myImgClip.write_videofile("./temp_img_clips/" + str(i) + ".mp4", fps, preset="fast")
            #myImgClip.write_videofile("./temp_img_clips/" + str(i) + ".mp4", fps, preset="fast")
            i += 1

    # Create the clip
    index = 0
    while allVidsDuration > 0:
        if (index < len(selectedVids)):
            index += 1
        else:
            # We should never need this
            index = 0
    # end


    clip = VideoFileClip("/home/user/Downloads/vids/out.mpg", audio=False)
    print("duration: ", clip.duration)

    # Increment render counts for all elements, but only after rendering was successful
    if isRenderSuccessful:
        for element in selectedVids:
            vidsList[element] += 1
        mp3List[selectedMp3] += 1


