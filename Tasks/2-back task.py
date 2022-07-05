from psychopy import visual, core, monitors, event, sound, gui, logging
import os
import time
import csv
import sys, os, errno # to get file system encoding (used in setDir())
import numpy as np
import random
from collections import OrderedDict
import pandas as pd
import codecs
import re

#Change this to the path where you store the stimuli folders for the 2-back
PATH = "/Users/Louis/OneDrive/Smallwood/Scripts/2-back/WM Stimuli/"
STIMTYPES = ['BODY', 'BP1', 'BP2', 'BP3', 'FACES', 'SCENES1', 'SCENES2', 'TOOLS']

#This function and imgdicter() are here to make imgsampler cleaner.
def imglister(sample, ct):
    itemlist = []

    count = 0
    while count < ct:
        item = random.choice(sample)
        if item not in itemlist:
            itemlist.append(item)
            count += 1
        else: 
            continue

    return itemlist

def imgdicter(itemlist, dictlist, imgfldr, trialtype):
    for item in itemlist:
        itemdict = {}
        itemdict['stimulus type'] = imgfldr
        itemdict['image'] = item
        itemdict['trial type'] = trialtype
        if itemdict['trial type'] == 'target':
            itemdict['correct_ans'] = 1
        else:
            itemdict['correct_ans'] = 2
        dictlist.append(itemdict)
    
    return dictlist

#Randomly samples a set of images from a given stimulus folder, then from that set
#samples a set of repeats to be target trials and target-lure trials. Returns a list of
#dictionaries containing information on trial-type and stimulus-type.
def imgsampler(imgfldr, trial_num=10, target_num=2, tlure_num = 2):
    path = os.path.join(PATH, imgfldr)

    imgs = trial_num - (target_num + tlure_num)
    imglist = imglister(os.listdir(path), imgs)

    t_list = imglister(imglist, target_num)

    tlsample = [x for x in imglist if x not in t_list]
    tl_list = imglister(tlsample, tlure_num)

    imgdictlist1 = []

    imgdictlist2 = imgdicter(imglist, imgdictlist1, imgfldr, 'non-target')
    imgdictlist3 = imgdicter(t_list, imgdictlist2, imgfldr, 'target')
    imgdictlist = imgdicter(tl_list, imgdictlist3, imgfldr, 'target-lure')

    return imgdictlist

#Randomly samples a set of stimulus types to form the block-types of the task
def prep_blks(block_num=8):
    blklist = imglister(STIMTYPES, block_num)
    return blklist

#swaps the positions of items in a list.
def swapPos(itms, pos1, pos2):
    itms[pos1], itms[pos2] = itms[pos2], itms[pos1]
    return itms

#With prep_lures(), orders the images sampled by imgsampler into a proper block, adding information 
#regarding correct response in the form of a list of dictionaries (i.e., a list of trials). prep_targs()
#starts off by placing the target trials n number of trials ahead of their corresponding non-target trials.
def prep_targs(imgsample, n=2):
    targlist = [x for x in imgsample if x['trial type'] == 'target']

    for targ in targlist:
        for trial in imgsample:
            if trial['image'] == targ['image'] and trial['trial type'] == 'non-target':  
                trial['pair'] = targ['pair']

    for trial in imgsample:
        if trial['pair'] != None and trial['trial type'] == 'non-target':
            npos = imgsample.index(trial)
            for i in range(6, len(imgsample)):
                if imgsample[i]['pair'] == trial['pair'] and imgsample[i]['trial type'] == 'target':
                    print(npos + n)
                    print(i)
                    imgsample = swapPos(imgsample, npos + n, i)
                    break

    return imgsample

#prep_lures() takes the target-trial-corrected block and finishes it by placing target-lures in spaces:
#1)less than or greater than n # of trials relative to their corresponding non-target trial and 2)elsewhere to
#the target trial pairs. Finally, I just make sure that the target-lure trials occur after their corresponding
#non-target trials.
def prep_lures(imgsample, tlure_num=2, n=2):
    lurelist = [x for x in imgsample if x['trial type'] == 'target-lure']
    
    poslist = []
    for i in range(len(imgsample)):
        poslist.append(i)

    llist = []
    for lure in lurelist:
        for trial in imgsample:
            if trial['image'] == lure['image'] and trial['trial type'] == 'non-target':
                pos = imgsample.index(trial)
                poslist = [x for x in poslist if pos - x != n and x - pos != n]
                llist.append(pos)
            elif trial['trial type'] == 'target-lure':
                break
    
    targlist = []
    for trial in imgsample:
        if trial['pair'] != None:
            pos = imgsample.index(trial)
            targlist.append(pos)
    
    poslist = [x for x in poslist if x not in targlist]

    if len(poslist) > 2:
        lurepos = imglister(poslist, tlure_num)
    else:
        lurepos = poslist

    count = 0
    for i in range(7, len(imgsample)):
        if imgsample[i]['trial type'] == 'target-lure':
            imgsample = swapPos(imgsample, lurepos[count], i)
            count += 1
    
    for lpos in lurepos:
        lure = imgsample[lpos]
        for pos in llist:
            img = imgsample[pos]
            if lure['image'] == img['image']:
                if lpos < pos:
                    imgsample = swapPos(imgsample, lpos, pos)
                    break

    return imgsample

def prep_blk(imgsample, n=2, tlure_num=2):
    semitrials = prep_targs(imgsample=imgsample, n=n)
    trials = prep_lures(semitrials, n=n, tlure_num=tlure_num)
    return trials

#Takes a preset counterbalanced order of stimulus types, generating a block for each.
#Uses imgsampler() and prep_blk() to order the sampled images within each block into a 
#proper order with correct placement of targets and target lures. The set of blocks will
#be in the form of a list of lists of dictionaries (i.e., a list of blocks) to be shuffled.
def block_generator(block_order):
    blks = []
    for stimtype in block_order:
        imgs = imgsampler(stimtype)
        block = prep_blk(imgs)
        blks.append(block)

    return blks

#Takes a list of blocks and returns a list of trials in the now counterbalanced order 
#(after shuffling the blocks returned by block_generator()).
def block_remover(blockSet):
    result = []

    i = 0

    for block in blockSet:
        for trial in block:
            trial['expr_onset'] = i * 2.5
            i += 1

            result.append(trial)

    return result

#formats the created list of blocks into a csv file, which will be fed to psychopy
def new_csv_creator(dictList):
    newData = {}
    
    for d in dictList:
        
        keys = list(d.keys())

        for key in keys:
            value = d[key]

            if key in newData:
                newData[key].append(value)
            else:
                newData[key] = [value]

    df = pd.DataFrame(newData)
    csvName = "taskScripts/resources/2-back_task/2-back_blocks.csv"
    df.to_csv(os.path.join(os.getcwd(), csvName))
    return csvName

def parse_instructions(input_data):
    '''
    parse instruction into pages
    page break is #
    '''

    text = re.findall(r'([^#]+)', input_data) # match any chars except for #

    return text

def load_instruction(PATH):
    '''
    load and then parse instrucition
    return a list
    '''
    import os
    with codecs.open(os.path.join(os.path.join(os.getcwd(),"taskScripts/resources/hcp2back"), PATH), 'r', encoding='utf8') as f:
        input_data = f.read()

    text = parse_instructions(input_data)

    return text

class instructions(object):
    '''
    show instruction and wait for trigger
    '''
    
    def __init__(self, window, instruction_txt):
        self.window = window
        self.instruction_txt = load_instruction(instruction_txt)

        self.display = visual.TextStim(
                window, text='default text', font='Arial', height=0.08,
                name='instruction',
                pos=[0,0], wrapWidth=1100,
                color='black',
                ) #object to display instructions

        self.display.size = 0.8
       

    def show(self):
        # get instruction
        for i, cur in enumerate(self.instruction_txt):
            self.display.setText(cur)
            self.display.draw()
            self.window.flip()
            event.waitKeys(keyList=['return'])

def runexp1(timer, win, writer, resultdict, data, runtime):
    stimuli_file = data
    ### Initialize variables

    # file related

    expName = 'hcp_2back'
    # stimuli = 'new_math_stimuli'
    data_folder = 'data' + '_' +  expName

    # experiment details related
    expr_time = 2 # formal experiment, it is 1.45
    choi_time = 2  # formal experiment, it is 1.45
    blank_time = 0.1   # display a blank screen
    timelimit_deci = 2 # equal to the choi_time 1.45 (check)
    trial_time = expr_time + choi_time + blank_time  # each trial is 3s

    pretrialFixDur = 15.00;  # in seconds previous four fixation is 15s
    posttrialFixDur = 16.00; # in seconds the final fixation is 16s

    instru_key     = ['return','escape']
    choie_key_list = ['left','right','escape']  # 1 == left, 2 == right

    # window related
    # windows
    # assign the monitor name
    monitor_name = 'HP ProOne 600'

    # instruction, position height
    word_pos = (0,0.05)
    text_h   = 120
    # fixa_h     = 200
    instru_pos = (0,0)
    # instru_h =100
    choice_right_pos =(-0.1,-0.05)
    choice_left_pos =(0.1,-0.05)

    ### define functions

    #write to resultdict
    def resultdictWriter(timepoint,timer,writer, iscorrect=None):
        resultdict['Timepoint'], resultdict['Time'], resultdict['Is_correct'] = timepoint, timer.getTime(), iscorrect
        writer.writerow(resultdict)
        resultdict['Timepoint'], resultdict['Time'] = None,None

    # get the current directory of this script - correct
    def get_pwd():
        global curr_dic
        curr_dic = os.path.dirname(sys.argv[0])  # U:/task_fMRI_Experiment/exp_March
        return curr_dic

    def shutdown ():
        win.close()
        core.quit()

    # Open a csv file, read through from the first row   # correct
    def load_conditions_dict(conditionfile):

    #load each row as a dictionary with the headers as the keys
    #save the headers in its original order for data saving

    # csv.DictReader(f,fieldnames = None): create an object that operates like a regular reader 
    # but maps the information in each row to an OrderedDict whose keys
    # are given by the optional fieldnames parameter.

        with open(os.path.join(os.getcwd(), conditionfile)) as csvfile:
            reader = csv.DictReader(csvfile)
            trials = []

            for row in reader:
                trials.append(row)
        
        # save field names as a list in order
            fieldnames = reader.fieldnames  # filenames is the first row, which used as keys of trials

        return trials, fieldnames   # trial is a list, each element is a key-value pair. Key is the 
                                    # header of that column and value is the corresponding value               


    # set up the window
    # fullscr: better timing can be achieved in full-screen mode
    # allowGUI: if set to False, window will be drawn with no frame and no buttons to close etc...

    def set_up_window(window=win): 
        mon = monitors.Monitor(monitor_name)
        mon.setDistance (114)
        win = window
        win.mouseVisible = False
        return win

    # prepare the content on the screen
    # removed height from function
    def prep_cont(line, pos):
        line_text = visual.TextStim(win, line, color='black', pos=pos, bold=True)
        return line_text

    def prep_image(imgfldr, image, pos, path=PATH):
        #path is the folder containing the stimuli for the task,
        #imagefolder is the folder containing the stimuli from the block,
        #image is the name of the exact stimulus being presented.
        imstim = visual.ImageStim(win,image = os.path.join(path,imgfldr,image), pos=pos)
        return imstim 
        
    # display each trial on the screen at the appropriate time
    def run_stimuli(stimuli_file, runtime):
        # read the stimuli  # re-define, not use numbers, but use keywords
            
        all_trials, headers = load_conditions_dict(conditionfile=stimuli_file)
        headers += ['i_trial_onset','trial_onset','choice_onset','blank_r_onset', 'RT', 'correct','KeyPress']   
        
        # prepare fixation and blank screen for drawing
        fixa = prep_cont('+',word_pos)
        blank = prep_cont(' ',word_pos)

        #prepare trial choices for drawing
        choice_l = prep_cont('SAME AS 2-BACK', choice_left_pos)
        choice_r = prep_cont('NOT SAME AS 2-BACK', choice_right_pos)
    
        # write the fixation time into the fixation.csv file    
        fixa_numth = 1  
        blockfixa_onset_abs = 0
        #f.write('%f,%.2f\n'% (fixa_numth, blockfixa_onset_abs))
        # draw the first long fixation and flip the window 

        fixa.draw()
        resultdictWriter('fixation cross', timer,writer)
        timetodraw = core.monotonicClock.getTime()
        #        
        while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
            pass
        
        run_onset = win.flip()  # this is when the real experiment starts and the run starts
        
        
        timetodraw = run_onset + pretrialFixDur
        # while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
        #     pass
        
        count = 1 # initiaze count
        curtime = core.Clock()
        for trial in all_trials:
            fixa.draw()
            win.flip()
            time.sleep(2)
            if curtime.getTime() < runtime:
                
                #''' trial is a ordered dictionary. The key is the first raw of the stimuli csv file'''
                expression = prep_image(trial['stimtype'],trial['image'],word_pos)
                # choice = prep_cont(trial['choice'][0:4],choice_right_pos)
                # choice_right = prep_cont(trial['choice'][len(trial['choice'])-4::],choice_left_pos)

                # display expression - the start of a new trial
                expression.draw()
                choice_l.draw()
                choice_r.draw()
                resultdictWriter('2-back Trial Start',timer,writer)
                resultdictWriter('Choice presented',timer,writer)
                # ideal_trial_onset = float( pretrialFixDur) +float(run_onset) + float( trial['expr_onset'])
                # timetodraw = ideal_trial_onset
                # while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
                #     pass
                trial_onset = win.flip()  # when expression is displayed, this is the trial onset
                timetodraw = trial_onset + expr_time
                while core.monotonicClock.getTime() < (timetodraw - (1/120.0)):
                        pass
                event.clearEvents()
                choice_onset = win.flip()
                keys = event.waitKeys(maxWait = timelimit_deci, keyList =['left','right'],timeStamped = True)
                fixa.draw()
                win.flip()
                resultdictWriter('Choice made',timer,writer)
                
                
                # display choice and ask subjects to press the button 1 or 2


                # If subjects do not press the key within maxwait time, RT is the timilimit and key is none and it is false
                if keys is None:
                    RT = 'None'
                    keypress = 'None'
                    correct = 'False'

            # If subjects press the key, record which key is pressed, RT and whether it is right
                elif type(keys) is list:
                    if keys[0][0]=='escape':
                        shutdown()
                    
                    else:
                        keypress = keys[0][0]
                        RT = keys[0][1] - choice_onset  
                        if trial["correct_ans"] == '1':
                            trial["correct_ans"] = 'left'
                        if trial["correct_ans"] == '2':
                            trial["correct_ans"] = 'right'
                        correct = (keys[0][0]==trial['correct_ans']) 
                        trial['RT']=RT
                        trial['correct'] = correct
                        trial['KeyPress'] = keypress
                        
                        resultdictWriter('2-back Trial End',timer,writer, correct)

            
                # trial['i_trial_onset'] = float( pretrialFixDur) + float( trial['expr_onset'])
                trial['trial_onset']   = trial_onset - run_onset
                trial['choice_onset']  = choice_onset - run_onset
                trial['RT'] = RT
                trial['correct'] = correct
                trial['KeyPress'] = keypress

                resultdictWriter('2-back Trial End',timer,writer, correct)
        
                count+=1 # the number-th trials that are displaying
            else:
                return

    # -----------------------------------------------------------------------------------------------------------------------------------------------
    # call the functions defined
    # get the current directory
    curr_dic = get_pwd()

    # set up the window to display the instruction
    win = set_up_window()

    # read the instruction
    #instruct()

    # generate the jitter list for the fixation and probe
    # know the number of trials
    #trials, fieldnames = load_conditions_dict(stimuli_file)

    text_inst = visual.TextStim(win=win, name='text_4',
        text='You may now stop.',
        font='Open Sans',
        pos=(0, 0), height=0.1, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    # show the instruction
    # instruct(curr_dic,instruct_figure)
    with open(os.path.join(os.getcwd(),"taskScripts/resources/2-back_Task/instr1.txt")) as f:
        lines1 = f.read()
    with open(os.path.join(os.getcwd(),"taskScripts/resources/2-back_Task/instr2.txt")) as f:
        lines2 = f.read()
    with open(os.path.join(os.getcwd(),"taskScripts/resources/2-back_Task/instr3.txt")) as f:
        lines3 = f.read()
        
        for i, cur in enumerate([lines1,lines2,lines3]):
            text_inst.setText(cur)
            text_inst.draw()
            win.flip()
            event.waitKeys(keyList=['return'])

    resultdictWriter('2-back Task Start',timer,writer)


    # run the stimuli
    run_stimuli(stimuli_file, runtime)

    ## end of the experiment
    #end_exp()
    resultdictWriter('2-back Task End',timer,writer)

def runexp(filename, timer, win, writer, resdict, runtime, seed):
    random.seed(a=seed)
    blk_order = prep_blks()
    data = block_generator(blk_order)
    random.shuffle(data)
    data = block_remover(data)
    data = new_csv_creator(data)
    resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : None, 'Task Iteration': None, 'Participant ID': None,'Response_Key':None, 'Auxillary Data': None}
    timer = core.Clock()
    runexp1(timer, win, writer, resdict,  data, runtime)