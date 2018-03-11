# UVH-program#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from psychopy import visual, event, core
from Tkinter import *
import random
import datetime
import time
import os
import unicodedata
import multiprocessing as mp
import serial
import csv
import re

################################################################
#
#                SETTINGS
#
################################################################
# ### MONITOR AND WINDOW

# for debugging process it is recomendened not to use fulscreen
fullscr = True
color_background = [0, 0, 0]

# width and height of the window in pixels (it matters only if fullscr == False
win_width, win_height = 1366, 768
#win_width, win_height = 1000, 600

# ### END OF MONITOR AND WINDOW
################################

################################
# ### STIMULI SETTINGS

group = 1      #1/2    1 - no background; 2 - with background
fontsize_instruction = 35
color_font = 'white'
bolded_font = False
word_index = 0

# time before first stimulus appears, after instruction (in seconds)  ## !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
init_gap_time = 2.0

# stimulus display time
stim_time = 5

# Inter Trial Interval, time between stimuli 
iti = 2
#iti = 0

# ### END OF STIMULI SETTINGS
################################ c mcm, kmfk    

################################################################
#
#                END of SETTINGS
#
################################################################


################################################################
#
#               PRELIMINARIES
#
################################################################

################################
# ### FUNCTION BOARD


def move_on():
    global keys_list
    while True:
        keys_list = event.getKeys()
        if 'space' in keys_list:
            break
        elif 'escape' in keys_list:
            mywin.close()
            core.quit()
            break

def create_slide(entry, color, height, x, y):
    text = {'intro': u'Przeczytaj uważnie instrukcję i postępuj zgodnie ze wskazówkami w niej zawartymi przez cały czas trwania badania.\n\nAby przejść dalej naciśnij spację',  
            'intro2': u'Na ekranie będą pokazywane różne postacie. Twoim zadaniem jest przyglądanie się wyświetlanym obrazom, a następnie udzielenie odpowiedzi na pojawiające się pytania przy pomocy myszki. \n\nNie ma dobrych i złych odpowiedzi. W razie niepewności kieruj się pierwszą myślą. Każda postać pojawi się 3 razy. \n\nAby przejść dalej naciśnij spację',
            'intro3': u'Na początku, na końcu oraz pomiędzy obrazami będzie wyświetlany punkt fiksacyjny. W miarę możliwości, spoglądaj na niego.\n\nAby rozpocząć eksperyment naciśnij spację',
            'ready': u'Połóż rękę na myszce i przygotuj się',
            'question1':u'Na ile prezentowany model jest podobny do człowieka?',
            'question2':u'Na ile łatwo było Ci odpowiedzieć na poprzednie pytanie?',
            'question3':u'Oceń na ile komfortowo czujesz się oglądając model w prezentowanym środowisku:',
            'question4':u'Jaka jest twoja emocjonalna reakcja na prezentowany model?',
            'ans10': u'(1) zupełnie \nniepodobny do \nczłowieka',
            'ans11': u'(2) raczej \nniepodobny do \nczłowieka',
            'ans12': u'(3) zaczyna \nprzypominać \nczłowieka',
            'ans13': u'(4) raczej \npodobny do \nczłowieka',
            'ans14': u'(5) bardzo \npodobny do \nczłowieka',
            'ans20': u'(1) bardzo \nłatwo' ,
            'ans21': u'(2) łatwo',
            'ans22': u'(3) trudno',
            'ans23': u'(4) bardzo \ntrudno',
            'ans30': u'(1) bardzo \nkomfortowo', 
            'ans31': u'(2) dość \nkomfortowo', 
            'ans32': u'(3) neutralnie',
            'ans33': u'(4) niekomfortowo', 
            'ans34': u'(5) bardzo \nniekomfortowo',
            'ans40': u'Model wzbudza \nmój niepokój',
            'ans41': u'Neutralna',
            'ans42': u'Model wzbudza \nsympatię',
            'empty': '',
            'fix':'+',
            'end': u'Koniec eksperymentu. Dziękujemy za udział w badaniu. \n\nProszę, wypełnij dane osobowe w okienku.'
            }

    aslide = visual.TextStim(
        win=mywin,
        text=text[entry], font='Monospace', wrapWidth=win_width*0.9,
        # instruction text wrap is 90% of the window width
        pos=(x, y), height=height,
        color=color, bold=bolded_font
        )
    return aslide

def create_boxes(quantity, y, answer):
    boxes = []
    color = (0.6,0.6,0.6)
    x = -250
    if quantity == 5:
        x = -500
    elif quantity == 4:
        x = -375
    for i in range(quantity):
        if i == answer:
            color = (1, 1, 0)
        else:
            color = (0.6,0.6,0.6)
        boxes.append(visual.ShapeStim(mywin, units='pix', lineWidth=2, lineColor='white', lineColorSpace='rgb', 
        fillColor=color, fillColorSpace='rgb', vertices=((120, 60), (120, -60), (-120, -60), (-120, 60)), 
        pos=(x, y), size=1, ori=0.0, opacity=1.0, contrast=1.0, depth=1))
        boxes[i].draw()
        x += 250
    return boxes

def create_quest(number, quantity, height):
    ans = []
    x = -250
    if quantity == 5:
        x = -500
    elif quantity == 4:
        x = -375
    question = create_slide('question'+str(number), 'black', 32, 0, height); question.draw();
    for i in range(quantity):
        ans.append(create_slide('ans'+str(number)+str(i), 'black', 24, x, height-100))
        ans[i].draw();
        x += 250

def check_pressed(quantity, boxes):
    pressed = None
    stop = False
    for i in range(quantity):
        if mouse.isPressedIn(boxes[i],buttons=[0]):
                pressed = i
                stop = True
    return [stop, pressed]

def create_image(path):
    image = visual.ImageStim(
        win=mywin,
        image=path, mask=None, units='',
        pos=(0.0, 0.0), size=[1366,768], ori=0.0, color=(1.0, 1.0, 1.0), colorSpace='rgb',
        contrast=1.0, opacity=1.0, depth=0, interpolate=False, flipHoriz=False,
        flipVert=False, texRes=128, name=None, autoLog=None, maskParams=None
        )
    return image

def check_close():
    keys_list = event.getKeys()
    if not keys_list:
        pass
    if 'escape' in keys_list:
        mywin.close()
        core.quit()

def port_reader(q, quit):
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
    while quit.empty():
        try:
            q.put(ser.readline())
        except ser.SerialTimeoutException:
            print('Data could not be read')
        time.sleep(0.04) 

def output_creator(num, q, flag, quit):
    out_path = "GSR_data/"+str(num.get())+"_GSR.csv"
    while quit.empty():
        data = q.get()
        with open(out_path, 'a') as out_file:
            try:
                out_file.write(re.sub("[^0-9]", "", data)+","+str(int(flag.value))+"\n")
            except OSError:
                print "No file"

# ### END OF FUNCTION BOARD
################################

################################################################
#
#               END OF PRELIMINARIES
#
################################################################

out_path = "Dane.csv"
resp_number = ""
with open(out_path, 'a+') as out_file:
    if os.stat("Dane.csv").st_size == 0:
        resp_number = "1"
    else:
        reader = csv.reader(out_file, delimiter=",")
        num = ""
        for row in reader:
            num = row[0]
        resp_number = str(int(float(row[0])+1))

out_path2 = "GSR_data/"+str(resp_number)+"_GSR.csv"
with open(out_path2, 'a') as out_file2:
    try:
        out_file2.write("GSR, stim_present\n")
    except OSError:
        print "No file"


resp_n = mp.Queue()
gsr_data = mp.Queue()
quit = mp.Queue()
flag = mp.Value('d', 0)
proc1 = mp.Process(target=port_reader, args=(gsr_data, quit))
proc2 = mp.Process(target=output_creator, args=(resp_n, gsr_data, flag, quit))
resp_n.put(resp_number)
proc1.start()
proc2.start()

################################
# ### GENERATE STIMULI

no_background = ["model01.png", "model02.png", "model03.png", "model04.png", "model05.png", "model06.png", "model07.png", 
                 "model08.png", "model09.png", "model10.png", "model11.png", "model12.png"]

with_background = ["model01b.png", "model02b.png", "model03b.png", "model04b.png", "model05b.png", "model06b.png", "model07b.png", 
                   "model08b.png", "model09b.png", "model10b.png", "model11b.png", "model12b.png"]

answers = []
stim_nr = 0
order_output = []

SEED = int(time.time())
random.seed(SEED)
if group == 1: 
    stimulus_list = no_background
    path = "no_background/"
else:
    stimulus_list = with_background
    path = "with_backgrounds/"
random.shuffle(stimulus_list)

# ### END OF GENERATE STIMULI
################################

################################################################
#
#               EXPERIMENT
#
################################################################

# create main window
mywin = visual.Window(
    [win_width, win_height],
    monitor='testMonitor',
    winType='pyglet',
    units='pix',
    fullscr=fullscr,
    colorSpace='rgb',
    rgb=color_background,
    allowGUI=True
    )

# code the time to name file or variable
datetime = datetime.datetime.now().strftime("%Y.%m.%d (%H:%M)")

################################

# ### INSTRUCTION
slide = create_slide('intro', 'black', fontsize_instruction, 0, 0); slide.draw(); mywin.flip()
move_on()

slide = create_slide('intro2', 'black', fontsize_instruction, 0, 0); slide.draw(); mywin.flip()
move_on()

slide = create_slide('intro3', 'black', fontsize_instruction, 0, 0); slide.draw(); mywin.flip()
move_on()

slide = create_slide('ready', 'black', fontsize_instruction, 0, 0); slide.draw(); mywin.flip()
core.wait(4)

slide = create_slide('empty', 'white', fontsize_instruction, 0, 0); slide.draw(); mywin.flip()
core.wait(0.5)
# ### END OF INSTRUCTION
################################


################################
# ### EXPERIMENTAL SESSION
slide = create_slide('fix', 'black', fontsize_instruction, 0, 0); slide.draw(); mywin.flip()
core.wait(10)

mouse = event.Mouse(visible=True, newPos=None, win=None)

for i in range(len(stimulus_list)):
    stimulus = path + stimulus_list[i]
    stim_nr = int(stimulus_list[i][5]+stimulus_list[i][6])
    order_output.append(stim_nr)
    ans =[]
    RTs = []

    pressed1 = [False, 0]
    pressed2 = [False, 0]
    
    image = create_image(stimulus); image.draw();mywin.flip()
    flag.value = stim_nr
    core.wait(stim_time)
    
    boxes = create_boxes(5, 150, None)
    quest1 = create_quest(1, 5, 250)
    mywin.flip()
    flag.value = 0
    start = time.time()
    while True:
        check_close()
        pressed1 = check_pressed(5, boxes)   #return [True, pressed number] if a box was pressed; [False, None] if not pressed
        #pressed1[1] = 1
        #core.wait(0.5)
        #pressed1[0] = True
        if pressed1[0]:                     #if a box was pressed, break the loop
            end = time.time()
            RTs.append("%.4f" % (end - start))
            ans.append(pressed1[1])
            break
    boxes = create_boxes(5, 150, pressed1[1])
    quest1 = create_quest(1, 5, 250)
    boxes = create_boxes(4, -150, None)
    quest2 = create_quest(2, 4, -50)
    mywin.flip()
    start = time.time()
    while True:
        check_close()
        pressed2 = check_pressed(4, boxes)   #return [True, pressed number] if a box was pressed; [False, None] if not pressed
        #pressed2[1] = 1       #
        #core.wait(0.5)
        #pressed2[0] = True        
        if pressed2[0]:                     #if a box was pressed, break the loop
            end = time.time()
            RTs.append("%.4f" % (end - start))
            ans.append(pressed2[1])
            break
    boxes = create_boxes(5, 150, pressed1[1])
    quest1 = create_quest(1, 5, 250)
    boxes = create_boxes(4, -150, pressed2[1])
    quest2 = create_quest(2, 4, -50)
    mywin.flip()
    core.wait(iti)
    
    image.draw();mywin.flip()
    flag.value = stim_nr
    core.wait(stim_time)
    
    boxes = create_boxes(5, 150, None)
    quest1 = create_quest(3, 5, 250)
    mywin.flip()
    flag.value = 0
    start = time.time()
    while True:
        check_close()
        pressed1 = check_pressed(5, boxes)   #return [True, pressed number] if a box was pressed; [False, None] if not pressed
        #pressed1[1] = 1
        #core.wait(0.5)
        #pressed1[0] = True        
        if pressed1[0]:                     #if a box was pressed, break the loop
            end = time.time()
            RTs.append("%.4f" % (end - start))
            ans.append(pressed1[1])
            break
    boxes = create_boxes(5, 150, pressed1[1])
    quest1 = create_quest(3, 5, 250)
    boxes = create_boxes(3, -150, None)
    quest2 = create_quest(4, 3, -50)
    mywin.flip()
    start = time.time()
    while True:
        check_close()
        pressed2 = check_pressed(3, boxes)   #return [True, pressed number] if a box was pressed; [False, None] if not pressed
        #pressed2[1] = 1
        #core.wait(0.5)
        #pressed2[0] = True
        if pressed2[0]:                     #if a box was pressed, break the loop
            end = time.time()
            RTs.append("%.4f" % (end - start))
            ans.append(pressed2[1])
            break
    boxes = create_boxes(5, 150, pressed1[1])
    quest1 = create_quest(3, 5, 250)
    boxes = create_boxes(3, -150, pressed2[1])
    quest2 = create_quest(4, 3, -50)
    mywin.flip()
    core.wait(iti)

    image.draw();mywin.flip()
    flag.value = stim_nr
    core.wait(stim_time)

    slide = create_slide('fix', 'black', fontsize_instruction, 0, 0); slide.draw(); mywin.flip()
    flag.value = 0
    core.wait(iti)
    answers.append([stimulus_list[i],ans,RTs])

slide = create_slide('fix', 'black', fontsize_instruction, 0, 0); slide.draw(); mywin.flip()
core.wait(10)

#####################################
### closing GSR data collection
quit.put(1)
gsr_data.close()
resp_n.close()
quit.close()
proc1.terminate()
proc2.terminate()
###
#####################################

slide = create_slide('end', 'black', fontsize_instruction, 0, 0); slide.draw(); mywin.flip()
core.wait(5)
mywin.winHandle.minimize()
mywin.winHandle.set_fullscreen(False)

# ### END OF EXPERIMENTAL SESSION
################################

################################################################
#
#                   CSV OUTPUT & EXTERNAL DATA
#
################################################################

################################
# ### EXTERNAL DATA
def button_action(event):
    global age, gender, educ, field
    age = entryAge.get()
    gender = entryGender.get()
    educ = entryEduc.get()
    field = entryField.get()
    if age != '' and gender != '' and educ != '' and field != '':
        masterTK.destroy()

masterTK = Tk()
masterTK.title(u"Dane osobowe")
masterTK.resizable(width=None, height=None)
mainFrame = Frame(masterTK)

labelFrame = Frame(mainFrame)
L = Label(labelFrame, text=u"Płeć: ", anchor=E).pack(fill=X)
L = Label(labelFrame, text=u"Wiek: ", anchor=E).pack(fill=X)
L = Label(labelFrame, text=u"Wykształcenie: ", anchor=E).pack(fill=X)
L = Label(labelFrame, text=u"Kierunek studiów (bieżący lub ukończony): ", anchor=E).pack(fill=X)

entryFrame = Frame(mainFrame)
entryGender = Entry(entryFrame)
entryGender.pack()
entryGender.focus_set()
entryAge = Entry(entryFrame)
entryAge.pack()
entryEduc = Entry(entryFrame)
entryEduc.pack()
entryField = Entry(entryFrame)
entryField.pack()


labelFrame.pack(side=LEFT)
entryFrame.pack(side=LEFT)
mainFrame.pack(side=TOP, expand=1, fill=X, padx=60, pady=5)
button1 = Button(masterTK, text=u"Zakończ")
button1.bind("<ButtonRelease-1>", button_action)
masterTK.bind("<Return>", button_action)

button1.pack(side=BOTTOM)

masterTK.withdraw()
masterTK.update_idletasks()  # Update "requested size" from geometry manager
x = (masterTK.winfo_screenwidth() - masterTK.winfo_reqwidth()) / 2
y = (masterTK.winfo_screenheight() - masterTK.winfo_reqheight()) / 2
masterTK.geometry("+%d+%d" % (x, y))
masterTK.deiconify()

masterTK.mainloop()

# ### END OF EXTERNAL DATA
################################

#################################
#  ### OUTPUT OPTIMISATION (UNSHUFFLE)

order = list(range(len(stimulus_list)))
random.seed(SEED)
random.shuffle(order)
output_list = [0] * len(stimulus_list)   # empty list with right length
for index, original_index in enumerate(order):
    output_list[original_index] = answers[index]

#  ### END OF OUTPUT OPTIMISATION  
################################

#################################
#  ### CSV OUTPUT

def no_poles(dirty_string):
    temp_string = ','.join(dirty_string).replace(u"\u0141", "L").replace(u"\u0142", "l")
    return unicodedata.normalize('NFKD', temp_string).encode('ascii', 'ignore')


def generate_stimuli_headers(f_output_list):
    stimuli_headers = ["id", "data", "plec", "wiek", "wyksztalcenie", "kierunek", "grupa", "kolejnosc"]
    for x in range(len(f_output_list)):
        for n in range(4):
            stimuli_headers.append(f_output_list[x][0] + "_pyt"+str(n+1))
        for n in range(4):
            stimuli_headers.append(f_output_list[x][0] + "_RT"+str(n+1))
    return no_poles(stimuli_headers)

def generate_data_logs(f_output_list):
    data_log = [resp_number, datetime, gender, age, educ, field, str(group), str(order_output).replace(",", ";")]
    for x in range(len(f_output_list)):
        for n in range(4):
            data_log.append(str(f_output_list[x][1][n]))
        for n in range(4):
            data_log.append(str(f_output_list[x][2][n]))
    return no_poles(data_log)

with open(out_path, 'a') as out_file:
    try:
        if os.stat("Dane.csv").st_size == 0:
            out_file.write((generate_stimuli_headers(output_list))+'\n')
        out_file.write(generate_data_logs(output_list) + '\n')
    except OSError:
        print "No file"

core.quit()

# ### END OF CSV OUTPUT
################################

################################################################
#
#               END OF EXPERIMENT
#
################################################################
