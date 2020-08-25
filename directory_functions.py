import os
import datetime
import contextlib

def ReadConfig(config):
    try:
        # Lock file can not exist
        assert not (os.path.isfile(config["root_path"] + "config.lock"))
        # Create lock
        lock = open(config["root_path"] + "config.lock", "w")
        lock.close()
        # Load config files into arrays / objects
        configFile = open(config["root_path"] + "config.conf", "r")
        fileContent = configFile.read()
        # Splitting up content into lines
        configLines = fileContent.split("\n")
        for line in configLines:
            # line.split(" = ")[0] : the conig name
            # line.split(" = ")[1] : the config parameter

            # EOF or wrong config entry
            if " = " not in line:
                break

            if (line.split(" = ")[1]).isnumeric():
                config[str(line.split(" = ")[0])] = int(line.split(" = ")[1])
            else:
                config[str(line.split(" = ")[0])] = line.split(" = ")[1]

        # Print the config dictionary
        print("Edit config.conf to change the settings.  Current config:")
        for entry in config:
            print("  " + entry + " = " + str(config[entry]))
        print("\n\n")
        configFile.close()
        # Delete lock
        os.remove(config["root_path"] + "config.lock")
    except:
        print("WARNING: Lock file exists. File can not be opened. (config.conf)")
        with contextlib.suppress(FileNotFoundError):
            os.remove(config["root_path"] + "config.lock")


def ReadLists(config, vidsList, mp3List, clipsList):
    try:
        # Make sure that files are not being written at the moment
        assert not os.path.isfile(config["root_path"] + "vids.lock")
        assert not os.path.isfile(config["root_path"] + "mp3.lock")
        assert not os.path.isfile(config["root_path"] + "clips.lock")
        # Check which files we already scanned. We store them in 2 dat files, 'vids.dat', 'mp3.dat'
        # Create locks
        lock1 = open(config["root_path"] + "vids.lock", "w")
        lock2 = open(config["root_path"] + "mp3.lock", "w")
        lock3 = open(config["root_path"] + "clips.lock", "w")
        lock1.close()
        lock2.close()
        lock3.close()
        vidsDat = open(config["root_path"] + "vids.dat", "r")
        mp3Dat = open(config["root_path"] + "mp3.dat", "r")
        clipsDat = open(config["root_path"] + "clips.dat", "r")
        vidsContent = vidsDat.read()
        mp3Content = mp3Dat.read()
        clipsContent = clipsDat.read()

        # Now we should have the content of both files
        # Splitting up content into lines
        vidsLines = vidsContent.split("\n")
        mp3Lines = mp3Content.split("\n")
        clipsLines = clipsContent.split("\n")
        # Processing the vids file content. File name and render-number is separated by TAB
        for line in vidsLines:
            # print("line", line.split("\t")[1])
            if "\t" in line:
                vidsList[line.split("\t")[0]] = int(line.split("\t")[1])
            else:
                print("This line is not processable (from vids.dat) (Probably this is an empty line) ")
        # Processing the mp3 file content. File name and render-number is separated by TAB
        for line in mp3Lines:
            if "\t" in line:
                mp3List[line.split("\t")[0]] = int(line.split("\t")[1])
            else:
                print("This line is not processable (from mp3.dat) (Probably this is an empty line) ")

        # Processing the clips file content. File name and name of mp3 is separated by TAB
        for line in clipsLines:
            if "\t" in line:
                clipsList[line.split("\t")[0]] = line.split("\t")[1]
            else:
                print("This line is not processable (from clips.dat) (Probably this is an empty line) ")

        # At this point, we should have the file contents stored in 3 dictionaries
        print("At this point, we should have the file contents stored in 3 dictionaries")
        print("vids", vidsList)
        print("mp3", mp3List)
        print("clips", clipsList)
        vidsDat.close()
        mp3Dat.close()
        clipsDat.close()
        # Delete locks
        os.remove(config["root_path"] + "vids.lock")
        os.remove(config["root_path"] + "mp3.lock")
        os.remove(config["root_path"] + "clips.lock")
    except:
        print("WARNING: One or more lock file exist for vids.dat, mp3.dat, clips.dat. Most likely these files are being written at the moment. Files can not be opened. ReadLists() will skip.")
        with contextlib.suppress(FileNotFoundError):
            os.remove(config["root_path"] + "vids.lock")
            os.remove(config["root_path"] + "mp3.lock")
            os.remove(config["root_path"] + "clips.lock")


def WriteConfig(config):
    try:
        # Lock file can not exist
        assert not (os.path.isfile(config["root_path"] + "config.lock"))
        # Create lock
        lock = open(config["root_path"] + "config.lock", "w")
        lock.close()
        # Open config file, save config object to file
        configFile = open(config["root_path"] + "config.conf", "w")
        for key in config:
            configFile.write(key + " = " + str(config[key]) + "\n")
        configFile.close()
        # Delete lock
        os.remove(config["root_path"] + "config.lock")
        return True
    except:
        print("WARNING: Lock file exists. Changes were not written to prevent data loss. (config.conf)")
        return False


def WriteLists(config, vidsList, mp3List, clipsList):
    allSuccessfull = True

    # Write vids
    try:
        # Lock file can not exist
        assert not (os.path.isfile(config["root_path"] + "vids.lock"))
        # Createe lock
        lock = open(config["root_path"] + "vids.lock", "w")
        lock.close()
        # Open vids.dat file, overwrite content
        vidsFile = open(config["root_path"] + "vids.dat", "w")
        for key in vidsList:
            vidsFile.write(key + "\t" + str(vidsList[key]) + "\n")
        vidsFile.close()
        # Delete lock
        os.remove(config["root_path"] + "vids.lock")
    except:
        print("WARNING: Lock file exists. Changes were not written to prevent data loss. (vids.dat)")
        with contextlib.suppress(FileNotFoundError):
            os.remove(config["root_path"] + "vids.lock")
        allSuccessfull = False

    # Write mp3
    try:
        # Lock file can not exist
        assert not (os.path.isfile(config["root_path"] + "mp3.lock"))
        # Createe lock
        lock = open(config["root_path"] + "mp3.lock", "w")
        lock.close()
        # Open mp3.dat file, overwrite content
        mp3File = open(config["root_path"] + "mp3.dat", "w")
        for key in mp3List:
            mp3File.write(key + "\t" + str(mp3List[key]) + "\n")
        mp3File.close()
        # Delete lock
        os.remove(config["root_path"] + "mp3.lock")
    except:
        print("WARNING: Lock file exists. Changes were not written to prevent data loss. (mp3.dat)")
        with contextlib.suppress(FileNotFoundError):
            os.remove(config["root_path"] + "mp3.lock")
        allSuccessfull = False

    # Write clips
    try:
        # Lock file can not exist
        assert not (os.path.isfile(config["root_path"] + "clips.lock"))
        # Createe lock
        lock = open(config["root_path"] + "clips.lock", "w")
        lock.close()
        # Open clips.dat file, overwrite content
        print("What is the content of clipsList?")
        print(clipsList)
        clipsFile = open(config["root_path"] + "clips.dat", "w")
        for key in clipsList:
            clipsFile.write(key + "\t" + clipsList[key] + "\n")
        clipsFile.close()
        # Delete lock
        os.remove(config["root_path"] + "clips.lock")
    except:
        print("WARNING: Lock file exists. Changes were not written to prevent data loss. (clips.dat)")
        with contextlib.suppress(FileNotFoundError):
            os.remove(config["root_path"] + "clips.lock")
        allSuccessfull = False
    return allSuccessfull

def CheckNewFiles(config, vidsList, mp3List):
    # Log file
    mainLog = open(config["root_path"] + "logs/main.log", "a+")
    now = str(datetime.datetime.now()).rsplit(".", 1)[0]

    # Scan the folders for files
    currentVids = os.listdir(config["vids_path"])
    currentMp3 = os.listdir(config["mp3_path"])

    # We need to close the files at the end, if open
    isVidsFileOpen = False
    isMp3FileOpen = False
    # Only open files if there are new elements.
    if len(currentVids) != len(vidsList):
        vidsDat = open(config["root_path"] + "vids.dat", "a+")
        isVidsFileOpen = True
    if len(currentMp3) != len(mp3List):
        mp3Dat = open(config["root_path"] + "mp3.dat", "a+")
        isMp3FileOpen = True

    # Decide which files are new
    for entry in currentVids:
        if entry in vidsList or entry == ".gitkeep":
            # We don't need to do anything, file already is on our list
            # If we find ".gitkeep", we skip
            continue
        else:
            # New video has been rendered 0 times in clips
            vidsList[entry] = 0
            # Save to file
            vidsDat.write(entry + "\t" + "0\n")

    for entry in currentMp3:
        if entry in mp3List or entry == ".gitkeep":
            # We don't need to do anything, file already is on our list
            # If we find ".gitkeep", we skip
            continue
        else:
            # New video has been rendered 0 times in clips
            mp3List[entry] = 0
            # Save to file
            mp3Dat.write(entry + "\t" + "0\n")


    # Close files, if open
    if isMp3FileOpen:
        mp3Dat.close()
        mainLog.write(now + " Wrote new elements to mp3.dat\n")

    if isVidsFileOpen:
        vidsDat.close()
        mainLog.write(now + " Wrote new elements to vids.dat\n")

    mainLog.close()
