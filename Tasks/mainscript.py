#  TODO LIST:
#         DONE 1.	Experience sampling questions need to be shown in a random order and to show all 14.
#         DONE 2.	Instead of using a completely random order, we would be better doing blocks of each task in a row as this will be easier for the participants. The tasks also for pairs (self + other, easy maths + hard maths, 1 back 0 back, go no go and finger tapping, reading and memory). Ideally it would be ordered so that we first pick a pair of tasks and then randomize which pair goes first.
#         DONE 3.	Change both the instructions and response keys for the maths task, 1 back and 0 back to left and right arrow keys.
#         DONE 4.	The 1 back and 0 back task ends with a screen that says remain the scanner. We should reombve this.
#         DONE 5.	The maths task should wait for a response before moving to the next trial
#         DONE 6.	The maths task starts and ends with a very long fixation cross. This should be removed
#         DONE 7.	The instructions for the 1 back and 0 back task did not fit on the screen of my computer
#         QUESTION - NO REPEATING OF STIMULI ACROSS TRIALS OR WITHIN      8.	There are repeating stimuli in the self and other tasks. We should show new items on every trial
#         DONE 9.	In the reading task the sentences do not complete before moving to the next trial. We should show complete sentences before moving on.
#         DONE 10.	In the introduction to the go / no go task it would help if we showed the participants examples of these trials types when we give them the instructions. This could just be done by making an image with examples of both on the left and right with the words respond and do not respond beneath the appropriate item.
#         DONE 11.	When the tapping task describes which hand to use it should say "Now tap in time with the grey square using you left/right hand"
#         DONE 12.	The reading task repeated exactly the same sentences on each block. It should show different ones every time. 
#         13.	I think we may need to rethink the memory task. Instead of asking them to type in the word, we should instead have a list of events (like party) and then we ask the participants first pick a party that they went to and then remember this event when the fixation cross is on the screen. Ideally this screen could show the cue on screen so help them remember what they are thinking about. I am going to email Meichao for the list of words she used so you can use these.
#         14.	It does not include videos yet. If it easier you can have a different script for this and we can either run that before or after the main one, or add it to this one. 




# Main script written by Ian Goodall-Halliwell. Subscripts are individually credited. Many have been extensively modified, for better or for worse (probably for worse o__o ).

from psychopy import core, visual, gui, event
import psychopy
import time
import csv
import taskScripts
import os
import random
os.chdir(os.path.dirname(os.path.realpath(__file__)))
# This class is responsible for creating and holding the information about how each task should run.
# It contains the number of repetitions and a global runtime variable.
# It also contains the subject ID, and will eventually use the experiment seed to randomize trial order.
class metadatacollection():
        def __init__(self, INFO, main_log_location):
                self.INFO = INFO
                self.main_log_location = main_log_location

                # Don't really know what this is, best to leave it be probably
                self.sbINFO = "Test"


        # This opens the GUI        
        def rungui(self):
                self.sbINFO = gui.DlgFromDict(self.INFO)

        # This writes info collected from the GUI into the logfile
        def collect_metadata(self):  
                print(os.getcwd())
                if os.path.exists(self.main_log_location): 
                        os.remove(self.main_log_location)
                f = open(self.main_log_location, 'w')
                metawriter = csv.writer(f)
                metawriter.writerow(["METADATA:"])
                metawriter.writerow(self.sbINFO.inputFieldNames)
                metawriter.writerow(self.sbINFO.data)
                random.seed(a=int(metacoll.INFO['Experiment Seed']))
                metawriter.writerow([taskbattery.time.getTime()])
                writer = csv.DictWriter(f, fieldnames=taskbattery.resultdict)
                writer.writeheader()
                f.close()
        
        
# Creates a list of all the tasks, and allows you to iterate through them without closing the window
class taskbattery(metadatacollection):
        time = core.Clock()
        resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : None, 'Task Iteration': None, 'Participant ID': None, 'Response_Key':None, 'Auxillary Data': None}
        #self.win = visual.Window(size=(1280, 800),color='white', winType='pyglet',fullscr=True)
        def __init__(self, tasklist, ESQtask, INFO):
                self.tasklist = tasklist
                self.ESQtask = ESQtask
                self.INFO = INFO
                self.taskexeclist = []
                self.win = visual.Window(size=(1280, 800),color='white', winType='pyglet',fullscr=False)
                self.text = text_2 = visual.TextStim(win=self.win, name='text_2',
                        text='Experiment starting placeholder',
                        font='Arial',
                        anchorHoriz='center', anchorVert='center', wrapWidth=None, ori=0, 
                        color='black', colorSpace='rgb', opacity=1, 
                        languageStyle='LTR',
                        depth=0.0)
                taskbattery.win = self.win
        
        
        #def initializeBattery(self):
                #for i in self.tasklist:

        def run_battery(self):
                self.text.draw(self.win)
                self.win.flip()
                time.sleep(1)
                event.waitKeys(keyList=['return'])
                self.win.flip()
                
                
                for i in self.tasklist:
                        i.initvers()
                        i.setver()
                        i.run()
                        self.ESQtask.run()
#OPEN THE TRIAL FILES AND CUT THEM INTO BLOCKS

# This creates a class which feeds all the necessary information into the task functions imported from each task file
# Allows you to create different task instances, which will be useful for creating blocks (my current project)
# Saves the log file after each task. It takes some extra time, but it prevents a crash from corrupting the file
class task(taskbattery,metadatacollection):
        def __init__(self, task_module, main_log_location, backup_log_location,  name, trialclass, runtime, dfile, ver, esq=False):#, trialfile, ver):
                self.main_log_location = main_log_location
                self.backup_log_location = backup_log_location # Not yet implemented
                self.task_module = task_module # The imported task function
                self.name = name # A name for each task to be written in the logfile
                
                self.trialclass = trialclass # Has something to do with writing task name into the logfile I think? Probably don't touch this.
                self.runtime = runtime # A "universal" "maximum" time each task can take. Will not stop mid trial, but will prevent trial repetions after the set time in seconds
                self.esq = esq
                self.ver = ver
                self.dfile = dfile
        print(os.getcwd())
        def initvers(self):
                cwd = os.path.dirname(os.path.abspath(__file__))  # Get the current working directory (cwd)
                print(cwd)
                os.chdir(cwd)
                try:
                        f = open(os.path.join(os.getcwd(), self.dfile), 'r')
                except:
                        f = open(os.path.join(os.path.join(os.getcwd(),'taskScripts'), self.dfile), 'r')
                d_reader = csv.DictReader(f)

                #get fieldnames from DictReader object and store in list
                self.headers = d_reader.fieldnames
                r = csv.reader(f)
                l = []
                for row in r:
                        l.append(row)
                        print(row)
                self.l = l
        def setver(self):
                ###
                ###   ###   NEED TO LOAD THE FILES FROM CSV AND PRESERVE THE HEADERS, THEN PUT THE OLD HEADERS INTO THE NEW BLOCK CSVs
                ###
                self.ver_a = random.sample(self.l, round(len(self.l)/2) )
                b = self.l
                for val in self.ver_a:
                        b[:] = [x for x in b if x != val]
                random.shuffle(b)
                b.insert(0,*[self.headers])
                self.ver_b = b
                random.shuffle(self.ver_a)
                
                self.ver_a.insert(0, self.headers)
                
                lis = [self.ver_a,self.ver_b]
                for enum, thing in enumerate(lis):
                        print(os.getcwd())
                        if not os.path.exists(os.getcwd()+ '//tmp'):
                                os.mkdir(os.getcwd()+ '//tmp')
                        if not os.path.exists(os.getcwd()+ '//tmp//%s' %(self.name)):
                                os.mkdir(os.getcwd() + '//tmp//%s' %(self.name))
                        if os.path.exists(os.getcwd() + '//tmp//%s' %(self.name + "//" + self.name + "_version_"+ str(enum) + ".csv")):
                                os.remove(os.getcwd() + '//tmp//%s' %(self.name + "//" + self.name + "_version_"+ str(enum) + ".csv"))
                        with open(os.getcwd() + '//tmp//%s' %(self.name + "//" + self.name + "_version_"+ str(enum) + ".csv"), mode='w') as file:
                                
                                file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                                for subthing in thing:
                                        file_writer.writerow(subthing)
                self._ver_a_name = os.getcwd() + '//tmp//%s' %(self.name + "//" + self.name + "_version_"+ str(0) + ".csv")
                self._ver_b_name = os.getcwd() + '//tmp//%s' %(self.name + "//" + self.name + "_version_"+ str(1) + ".csv")
                
                                
                                
        def run(self):
                if not os.path.exists(self.main_log_location):
                        if self.main_log_location.split(".")[1] == None:
                                os.mkdir(self.main_log_location.split("/")[0])      
                f = open(self.main_log_location, 'a')
                r = csv.writer(f)
                writer = csv.DictWriter(f, fieldnames=taskbattery.resultdict)
                r.writerow(["EXPERIMENT DATA:",self.name])
                r.writerow(["Start Time", taskbattery.time.getTime()])
                taskbattery.resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : self.name, 'Task Iteration': '1', 'Participant ID': self.trialclass[1], 'Response_Key' : None, 'Auxillary Data': None}
                if self.esq == False:
                        if self.ver == 1:
                                self.task_module.runexp(self.backup_log_location, taskbattery.time, taskbattery.win, writer, taskbattery.resultdict, self.runtime, self._ver_b_name, int(metacoll.INFO['Experiment Seed']))
                        if self.ver == 2:
                                self.task_module.runexp(self.backup_log_location, taskbattery.time, taskbattery.win, writer, taskbattery.resultdict, self.runtime, self._ver_b_name, int(metacoll.INFO['Experiment Seed']))
                if self.esq == True:
                        self.task_module.runexp(self.backup_log_location, taskbattery.time, taskbattery.win, writer, taskbattery.resultdict, self.runtime, None, int(metacoll.INFO['Experiment Seed']))
                f.close()
                taskbattery.resultdict = {'Timepoint': None, 'Time': None, 'Is_correct': None, 'Experience Sampling Question': None, 'Experience Sampling Response':None, 'Task' : None, 'Task Iteration': None, 'Participant ID': None,'Response_Key':None, 'Auxillary Data': None}




# Info Dict

INFO = {
                'Experiment Seed': '1',  
                'Subject': '2', 
                'Block Runtime': 70
                }






# Main and backup data file
datafile = str(os.path.dirname(os.path.realpath(__file__)) + '/log_file/testfull2.csv')
datafileBackup = 'log_file/testfullbackup.csv'

# Run the GUI and save output to logfile
metacoll = metadatacollection(INFO, datafile)
metacoll.rungui()
metacoll.collect_metadata()

# Defining each task as a task object
ESQTask = task(taskScripts.ESQ, datafile, datafileBackup, "Experience Sampling Questions", metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources/GoNoGo_Task/gonogo_stimuli.csv',1, esq=True)
friendTask = task(taskScripts.otherTask, datafile, datafileBackup, "Friend Task", metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'taskScripts/resources/Other_Task/Other_Stimuli.csv', 1)
youTask = task(taskScripts.selfTask, datafile, datafileBackup, "You Task", metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources/Self_Task/Self_Stimuli.csv', 1)
gonogoTask = task(taskScripts.gonogoTask, datafile, datafileBackup, "GoNoGo Task", metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources/GoNoGo_Task/gonogo_stimuli.csv', 1)
fingertapTask = task(taskScripts.fingertappingTask, datafile, datafileBackup, "Finger Tapping Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources/GoNoGo_Task/gonogo_stimuli.csv', 1)
readingTask = task(taskScripts.readingTask, datafile, datafileBackup, "Reading Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),"taskScripts/resources/Reading_Task/sem_stim_run.csv", 1)
memTask = task(taskScripts.memoryTask, datafile, datafileBackup,"Memory Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'taskScripts/resources/Memory_Task/Memory_prompts.csv', 1)
zerobackTask = task(taskScripts.zerobackTask, datafile, datafileBackup,"Zero-Back Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources//ZeroBack_Task//ConditionsSpecifications_ES_zeroback.csv', 1)
onebackTask = task(taskScripts.onebackTask, datafile, datafileBackup,"One-Back Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources//ZeroBack_Task//ConditionsSpecifications_ES_oneback.csv', 1)
easymathTask1 = task(taskScripts.easymathTask, datafile, datafileBackup,"Math Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),"taskScripts/resources/Maths_Task/new_math_stimuli1.csv", 1)
hardmathTask1 = task(taskScripts.hardmathTask, datafile, datafileBackup,"Math Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),"taskScripts/resources/Maths_Task/new_math_stimuli2.csv", 1)
#Block 2

friendTask2 = task(taskScripts.otherTask, datafile, datafileBackup, "Friend Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources/Other_Task/Other_Stimuli.csv', 2)
youTask2 = task(taskScripts.selfTask, datafile, datafileBackup, "You Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources/Self_Task/Self_Stimuli.csv', 2)
gonogoTask2 = task(taskScripts.gonogoTask, datafile, datafileBackup, "GoNoGo Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources/GoNoGo_Task/gonogo_stimuli.csv', 2)
fingertapTask2 = task(taskScripts.fingertappingTask, datafile, datafileBackup, "Finger Tapping Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources/GoNoGo_Task/gonogo_stimuli.csv', 2)
readingTask2 = task(taskScripts.readingTask, datafile, datafileBackup, "Reading Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),"taskScripts/resources/Reading_Task/sem_stim_run.csv", 2)
memTask2 = task(taskScripts.memoryTask, datafile, datafileBackup,"Memory Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources/Memory_Task/Memory_prompts.csv', 2)
zerobackTask2 = task(taskScripts.zerobackTask, datafile, datafileBackup,"Zero-Back Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources//ZeroBack_Task//ConditionsSpecifications_ES_zeroback.csv', 2)
onebackTask2 = task(taskScripts.onebackTask, datafile, datafileBackup,"One-Back Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),'resources//ZeroBack_Task//ConditionsSpecifications_ES_oneback.csv', 2)
easymathTask2 = task(taskScripts.easymathTask, datafile, datafileBackup,"Math Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),"taskScripts/resources/Maths_Task/new_math_stimuli1.csv", 2)
hardmathTask2 = task(taskScripts.hardmathTask, datafile, datafileBackup,"Math Task",  metacoll.sbINFO.data, int(metacoll.INFO['Block Runtime']),"taskScripts/resources/Maths_Task/new_math_stimuli2.csv", 2)
# Example of defining a full battery:
#tasks = list([friendTask2,youTask2,gonogoTask2,fingertapTask2,readingTask2,memTask])
fulltasklist = [
        [friendTask,youTask],[gonogoTask,fingertapTask],[readingTask,memTask],[zerobackTask,onebackTask],[easymathTask1,hardmathTask1],
        [friendTask2,youTask2],[gonogoTask2,fingertapTask2],[readingTask2,memTask2],[zerobackTask2,onebackTask2],[easymathTask2,hardmathTask2]]

for enum, blk in enumerate(fulltasklist):
        random.shuffle(blk)

random.shuffle(fulltasklist)
tasks = fulltasklist

tasks = [readingTask2]

# Example of task battery using 0-back and 1-back tasks:



# ADD AN INITIAL SCREEN DESCRIBING THE EXPERIMENT
# ADD DESCRIPTION FOR WHAT LEFT AND RIGHT DOES FOR THE SELF/OTHER TASK



tbt = taskbattery(tasks, ESQTask, INFO)
if __name__ == "__main__":
       tbt.run_battery()