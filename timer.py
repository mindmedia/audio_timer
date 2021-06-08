#!/usr/bin/python3

from tkinter import *
import alsaaudio
import audioop
from PIL import ImageTk

# to simulate keyboard input
from pynput.keyboard import Key, Controller

# For the reset button through the gpio of the raspberry.
from gpiozero import Button as piButton
resetButton = piButton(21, hold_time=4)
shutdownButton = piButton(13)

# For shuting down computer
import subprocess
import shlex

# Global variables.
started = False
seconds = 0
belowLow = 0
buttonClear = True
rms_val = 0


class App():
    
    def reset(self):
        global started
        global belowLow
        global seconds
        self.t.set("00")
        started = False
        seconds = 0
        belowLow = 0
        global buttonClear
        buttonClear = True
        return None
        
    def start(self):
        global started
        global buttonClear
        if started == False and buttonClear:
            started = True
            return self.timer()
        else:
            return None
    
    def stop(self):
        global started
        started = False
        global buttonClear
        buttonClear = False
        return None
     
    def timer(self):
        def seconds_timer():
            global started
            global seconds
            self.d = str(seconds).zfill(2)
            self.t.set(self.d)
            if started:
                self.root.after(1000,self.timer)
                seconds += 1       
        seconds_timer()
        
    def rms_display(self):
        def rms_refresh():  
            global rms_val
            self.rms.set(str(rms_val).zfill(4))
            self.root.after(100,self.rms_display)
        rms_refresh()
        
    def exit_screensaver(self):
        def check_button():
            if resetButton.is_active:
                keyboard = Controller()
                keyboard.press(Key.esc)
                keyboard.release(Key.esc)
                #print("Esc")
            self.root.after(100,self.exit_screensaver)
        check_button()
        
    def shutdown(self):
        def check_button():
            #if shutdownButton.is_held:
            if resetButton.is_held:
                #cmd = shlex.split("sudo shutdown -h now")
                cmd = shlex.split("sudo reboot")
                subprocess.call(cmd)
            self.root.after(100,self.shutdown)
        check_button()
                
    def listen(self):
        def listenActions():
            global rms_val
            #Take the audio stream and get the rms value
            input = self.p.read()
            rms_val = audioop.rms(input[1], 2)
            #print(f'RMS: {rms_val}')
            
            # If the rms value is higher than 1000, start the timer
            if rms_val > 1000:
                self.start()
                
            #If the rms is below 50, stop timer with delay
            elif rms_val < 50:
                # this is to give a 100 milisecond delay before stoping
                global belowLow 
                if started:
                    belowLow += 1
                if started and belowLow > 100:
                    self.stop()
                    
            global buttonClear        
            #To reset the timer using the gpio button        
            if resetButton.is_active and buttonClear == False:
                self.reset()
            self.root.after(1, self.listen)
        listenActions()

            
        
    def __init__(self):
        self.p = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device='default', cardindex=- 1)
        self.p.setchannels(1)
        self.p.setrate(44100)
        self.p.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.p.setperiodsize(160)
        
        self.root=Tk()
        
        render = ImageTk.PhotoImage(file="/home/pi/Documents/python_audio/images/scream_hd.jpg")
        canvas=Canvas(self.root,width=1920,height=1080)
        canvas.create_image(0,0,anchor=NW,image=render)
        canvas.pack() 

        #self.root.title("Laaaaaaaaa Laaaaaaaaa")
        self.root.overrideredirect(True) # removes title bar
        self.root.geometry("1920x1080")
        self.t = StringVar()
        self.t.set("00")
        self.rms = StringVar()
        self.rms.set("0")
        self.lb = Label(self.root,textvariable=self.t,font=("Courier 40 bold"),bg="black", fg="white")
        #self.bt3 = Button(self.root,text="Reset",command=self.reset,font=("Arial 12 bold"))
        self.lb.place(x=950,y=725)
        #self.bt3.place(x=370,y=200)
        self.rmsLabel = Label(self.root,textvariable=self.rms,font=("Courier 40 bold"),bg="red",fg="white")
        self.rmsLabel.place(x=2,y=995)
        #self.root.wm_attributes('-transparentcolor',"grey")
        self.listen()
        self.rms_display()
        self.exit_screensaver()
        self.shutdown()
        self.root.mainloop()

a = App()

  

  




