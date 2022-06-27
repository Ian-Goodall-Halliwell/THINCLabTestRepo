#Written by Brontë McKeown and Theodoros Karapanagiotidis
from psychopy import visual 
from psychopy.visual import MovieStim 
from psychopy import gui, data, core,event
import csv
import time
from time import localtime, strftime, gmtime
from datetime import datetime
import os.path
import pyglet 
import pandas as pd
from itertools import groupby
import random

###################################################################################################
def runexp(filename, timer, win, writer, resdict, runtime,dfile,seed):
# kill switch for Psychopy3
    random.seed(seed)
    resdict['Timepoint'], resdict['Time'] = 'Movie Task Start', timer.getTime()
    writer.writerow(resdict)
    resdict['Timepoint'], resdict['Time'] = None,None
    df = pd.read_csv(dfile) 
    
    

    

    # user can update instructions for task here if required.
    instructions = """You will be presented with several video clips. These clips are rated 15 and contain extreme violence, aggression and bad language. If you find these types of clips distressing, please do not participate in this study. 
    \nIf at any point, you become distressed and would like to stop the task, please inform the experimenter. You will not be penalised for withdrawing from the study. 
    \nAt the end of each task block, you will be asked to rate several statements about the ongoing thoughts you experienced during that block. 
    \nPress return to begin the experiment."""

    # user can update start screen text here if required. 
    start_screen = "The experiment is about to start. Press return to continue."


    
    # create text stimuli to be updated for start screen instructions.
    stim = visual.TextStim(win, "", color = [-1,-1,-1], wrapWidth = 1300, units = "pix", height=40)

    # update text stim to include instructions for task. 
    stim.setText(instructions)
    stim.draw()
    win.flip()
    # Wait for user to press enter to continue. 
    event.waitKeys(keyList=(['return']))

    # update text stim to include start screen for task. 
    stim.setText(start_screen)
    stim.draw()
    win.flip()
    
    # Wait for user to press enter to continue. 
    event.waitKeys(keyList=(['return']))
    control = []
    action = []
    try:
        # Create two lists, one with the control videos, and one with action videos
        # Videos are sorted based on their file name
        for a in os.listdir(os.path.join(os.getcwd(), 'taskScripts//resources//Movie_Task//videos')):
            v = a.split("_")[0]
            if v == "control":
                control.append(a)
            if v == "action":
                action.append(a)
        random.shuffle(control)
        random.shuffle(action)
       
        
        
        # Write when it's initialized
        resdict['Timepoint'], resdict['Time'] = 'Movie Init', timer.getTime()
        writer.writerow(resdict)
        resdict['Timepoint'], resdict['Time'] = None,None
        
        # Create two different lists of videos for trial 1 and trial 2. 
        filmlista = []
        filmlistb = []
        for en, m in enumerate(control):
            m = os.path.join(os.getcwd(), 'taskScripts//resources//Movie_Task//videos//' + m)
            r = os.path.join(os.getcwd(), 'taskScripts//resources//Movie_Task//videos//' + action[en])
            filmlista.append(m)
            filmlistb.append(r)
    
        
        
        #filmlist = random.choice([filmlista,filmlistb])
        
        # Pick the video to show based on the trial version, we are just going to pick the one at the top of the list
        if filename == 1:
            filmlist = filmlista[0]
        if filename == 2:
            filmlist = filmlistb[0]
            
        
        
        # present film using moviestim
        resdict['Timepoint'], resdict['Time'] = 'Movie Start', timer.getTime()
        writer.writerow(resdict)
        resdict['Timepoint'], resdict['Time'] = None,None
        
        
        mov = visual.MovieStim3(win, filmlist, size=(1920, 1080), flipVert=False, flipHoriz=False, loop=False)
        while mov.status != visual.FINISHED:
            mov.draw()
            win.flip()
        
    except:
        
        for a in os.listdir(os.path.join(os.getcwd(), 'resources//Movie_Task//videos')):
            v = a.split("_")[0]
            if v == "control":
                control.append(a)
            if v == "action":
                action.append(a)
        random.shuffle(control)
        random.shuffle(action)
       
        
        
        # Write when it's initialized
        resdict['Timepoint'], resdict['Time'] = 'Movie Init', timer.getTime()
        writer.writerow(resdict)
        resdict['Timepoint'], resdict['Time'] = None,None
        
        # Create two different lists of videos for trial 1 and trial 2. 
        filmlista = []
        filmlistb = []
        for en, m in enumerate(control):
            m = os.path.join(os.getcwd(), 'resources//Movie_Task//videos//' + m)
            r = os.path.join(os.getcwd(), 'resources//Movie_Task//videos//' + action[en])
            filmlista.append(m)
            filmlistb.append(r)
    
        
        
        #filmlist = random.choice([filmlista,filmlistb])
        
        # Pick the video to show based on the trial version, we are just going to pick the one at the top of the list
        if filename == 1:
            filmlist = filmlista[0]
        if filename == 2:
            filmlist = filmlistb[0]
            
        
        
        # present film using moviestim
        resdict['Timepoint'], resdict['Time'] = 'Movie Start', timer.getTime()
        writer.writerow(resdict)
        resdict['Timepoint'], resdict['Time'] = None,None
        
        
        mov = visual.MovieStim3(win, filmlist, size=(1920, 1080), flipVert=False, flipHoriz=False, loop=False)
        while mov.status != visual.FINISHED:
            mov.draw()
            win.flip()
    
    
    resdict['Timepoint'], resdict['Time'] = 'Movie End', timer.getTime()
    writer.writerow(resdict)
    resdict['Timepoint'], resdict['Time'] = None,None
    
