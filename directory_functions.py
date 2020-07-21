import os

def ReadConfig(config):
    # Load config files into arrays / objects
    configFile = open("config.conf", "r")
    fileContent = configFile.read()
    # Splitting up content into lines
    configLines = fileContent.split("\n")
    for line in configLines:
        # line.split(" = ")[0] : the conig name
        # line.split(" = ")[1] : the config parameter
        config[str(line.split(" = ")[0])] = line.split(" = ")[1]

    # Print the config dictionary
    print("Edit config.conf to change the settings.  Current config:")
    for entry in config:
        print("  " + entry + " = " + config[entry])
    print("\n\n")
    configFile.close()


def ReadLists(config, vidsList, mp3List, clipsList):
    # Check which files we already scanned. We store them in 2 dat files, 'vids.dat', 'mp3.dat'
    vidsDat = open("vids.dat", "r")
    mp3Dat  = open("mp3.dat", "r")
    clipsDat = open("clips.dat", "r")
    vidsContent = vidsDat.read()
    mp3Content = mp3Dat.read()
    clipsContent = clipsDat.read()

    # Now we should have the content of both files
    # Splitting up content into lines
    vidsLines = vidsContent.split("\n")
    mp3Lines = mp3Content.split("\n")
    clipsLines = clipsContent.split("\n")
    if (len(vidsList) > 0 and len(mp3Lines) > 0):
        # Processing the vids file content. File name and render-number is separated by TAB
        for line in vidsLines:
            vidsList[line.split("\t")[0]] = line.split("\t")[1]
        # Processing the mp3 file content. File name and render-number is separated by TAB
        for line in mp3Lines:
            mp3List[line.split("\t")[0]] = line.split("\t")[1]
    else:
        print("dat files are still empty")

    if (len(clipsList) > 0):
        # Processing the clips file content. File name and name of mp3 is separated by TAB
        for line in clipsLines:
            clipsList[line.split("\t")[0]] = line.split("\t")[1]

    # At this point, we should have the file contents stored in 3 dictionaries
    vidsDat.close()
    mp3Dat.close()
    clipsDat.close()


def CheckNewFiles(config, vidsList, mp3List):
    # Scan the folders for files
    currentVids = os.listdir(config["vids_path"])
    currentMp3 = os.listdir(config["mp3_path"])

    # We need to close the files at the end, if open
    isVidsFileOpen = False
    isMp3FileOpen = False
    # Only open files if there are new elements.
    if len(currentVids) != len(vidsList):
        vidsDat = open("vids.dat", "a")
        isVidsFileOpen = True
    if len(currentMp3) != len(mp3List):
        mp3Dat = open("mp3.dat", "a")
        isMp3FileOpen = True


    # Decide which files are new
    for entry in currentVids:
        if entry in vidsList:
            # We don't need to do anything, file already is on our list
            continue
        else:
            # New video has been rendered 0 times in clips
            vidsList[entry] = 0
            # Save to file
            vidsDat.write(entry + "\t" + "0\n")

    # Test
    # print("Current vidsList is:")
    # print(vidsList)

    for entry in currentMp3:
        if entry in mp3List:
            # We don't need to do anything, file already is on our list
            continue
        else:
            # New video has been rendered 0 times in clips
            mp3List[entry] = 0
            # Save to file
            mp3Dat.write(entry + "\t" + "0\n")

    # Test
    # print("Current mp3List is:")
    # print(mp3List)

    # Close files, if open
    if isMp3FileOpen:
        mp3Dat.close()
    if isVidsFileOpen:
        vidsDat.close()
