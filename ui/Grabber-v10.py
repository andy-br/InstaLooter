import time, threading
from tkinter import *
from tkinter import messagebox
import sys
import os
import subprocess
from instalooter.looters import ProfileLooter
import logging


class App(object):
    def __init__(self, master):
        master.geometry("400x300")
        master.title("Grabber")
        lbCommand = Label(master, text="Grabber", font=("Courier New", 16))
        lbCommand.grid(column=0, row=0, padx=13, sticky=(W))
        instruction = Label(master,
                            text="Enter the full path to the folder, minus the final forward slash: e.g. c:/users/computername/documents/projectfolder",
                            wraplength=320)
        instruction.grid(column=0, row=1, padx=13, pady=0, sticky=(W))
        App.folder = Entry(master, width=60)
        App.folder.grid(column=0, row=2, padx=13, pady=5, sticky=(W))
        instruction1 = Label(master, text="Enter a username to create a named folder and run the grabbing process:")
        instruction1.grid(column=0, row=3, padx=13, sticky=(W))
        App.videoOption = StringVar()
        videos = Checkbutton(master, text="Include Videos?", variable=App.videoOption, onvalue="-v", offvalue="")
        videos.grid(column=0, row=4, padx=13, pady=5, sticky=(W))
        App.username = Entry(master)
        App.username.grid(column=0, row=4, pady=5)
        grabber = Button(master, text="Grab User Images", command=processStart)
        grabber.grid(column=0, row=5, pady=0)
        instruction2 = Label(master, text="Click to close this window and let the current grab finish:")
        instruction2.grid(column=0, row=7, pady=5)
        exitButton = Button(master, text="Close", command=processStop)
        exitButton.grid(column=0, row=8, pady=0)
        updateButton = Button(master, text="Update", command=updateProcessStart)
        updateButton.grid(column=0, row=8, padx=13, pady=5, sticky=(W))
        App.messages = Label(master, text="Waiting For Request", fg="red", font="-weight bold")
        App.messages.grid(column=0, row=9, pady=3)


def postProcess():
    # si = subprocess.STARTUPINFO()
    # si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    # subprocess.call("python -m instalooter user %(1)s %(3)s -d -e %(2)s/%(1)s -T {username}--{datetime}" % {"1":App.username.get(), "2":App.folder.get(), "3":App.videoOption.get()}, startupinfo=si)

    workingfolder = App.folder.get() + "/" + App.username.get()

    looter = ProfileLooter(App.username.get())
    looter.dump_json = True
    looter.extended_dump = True

    logging.error("Username: " + App.username.get())
    logging.error("Folder: " + App.folder.get())
    logging.error("Video: " + App.videoOption.get())

    looter.download_pictures(workingfolder)

    if App.videoOption.get() == '-v':
        # looter.download_pictures(App.folder.get())
        pass

    createCSV()
    App.messages.configure(text="Process Complete")
    return


def update():
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    p = subprocess.Popen("pip install instalooter -U", startupinfo=si)
    time.sleep(30)
    p.terminate()
    p.wait()
    App.messages.configure(text="Module Updated")
    return


def processStart():
    # App.messages.configure(text=threading.activeCount())
    App.messages.configure(text="Processing..")
    Process = threading.Thread(target=postProcess)
    Process.start()


def updateProcessStart():
    App.messages.configure(text="Updating...")
    updateProcess = threading.Thread(target=update)
    updateProcess.start()


def processStop():
    os._exit(-1)


def createCSV():
    import glob
    import json
    import csv
    import datetime
    import re

    # read the json files in the directory
    filepath = "%(2)s/%(1)s/*.json" % {"1": App.username.get(), "2": App.folder.get()}
    outpath = "%(2)s/%(1)s/metadata.csv" % {"1": App.username.get(), "2": App.folder.get()}

    with open(outpath, 'w', newline='\n') as outcsv:
        writer1 = csv.writer(outcsv)
        writer1.writerow(
            ["Post URL", "Image Src", "Video Src", "Date/Time", "Likes", "Like Users", "Comment Count", "Video Views",
             "Post Caption", "Comments"])

    read_files = glob.glob(filepath)

    # declare a list vars
    main_object = []
    comment_object = []
    like_object = []

    for f in read_files:
        with open(f, 'r') as jsonfile:
            json_data = json.load(jsonfile)
            imagesrc = json_data['display_url']
            epochtimestamp = json_data['taken_at_timestamp']
            timestamp = datetime.datetime.utcfromtimestamp(epochtimestamp).strftime('%Y-%m-%d %H:%M:%S')
            likecount = 0
            commentcount = 0

            try:
                likecount = json_data['edge_media_preview_like']['count']
            except:
                pass

            try:
                commentcount = json_data['edge_media_to_comment']['count']
            except:
                pass

            try:
                for likeuser in json_data['edge_media_preview_like']['edges']:
                    like_object.append(likeuser['node']['username'])
            except:
                like_object = "No User"

            try:
                for comment in json_data['edge_media_to_comment']['edges']:
                    comment_object.append(comment['node']['text'])
                    comment_object.append(comment['node']['owner']['username'])
            except:
                comment_object = "No Comment"

            shortcode = json_data['shortcode']
            posturl = "https://www.instagram.com/p/" + shortcode

            try:
                videoviews = json_data['video_view_count']
            except KeyError:
                videoviews = "N/A"

            try:
                videosrc = json_data['video_url']
            except KeyError:
                videosrc = "N/A"

            try:
                caption = json_data['edge_media_to_caption']['edges'][0]['node']['text']
            except:
                caption = "No caption text"
            strippedcaption = re.sub('\n', '', caption)

            main_object.append(posturl)
            main_object.append(imagesrc)
            main_object.append(videosrc)
            main_object.append(timestamp)
            main_object.append(likecount)
            main_object.append(like_object)
            like_object = []
            main_object.append(commentcount)
            main_object.append(videoviews)
            main_object.append(strippedcaption)
            main_object.append(comment_object)
            comment_object = []

            with open(outpath, 'a', newline='\n', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                writer.writerow(main_object)
            main_object = []


mainWindow = Tk()
app = App(mainWindow)
mainWindow.mainloop()
finish = True
# Process.join()


