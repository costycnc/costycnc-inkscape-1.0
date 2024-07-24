import inkex,sys,math,time,ctypes,os
from inkex import bezier
from inkex.elements import Group, Line,Circle,PathElement
from datetime import datetime
from tkinter import messagebox as mb
import serial
import time

class hello(inkex.EffectExtension):


    def add_arguments(self, pars):
        pars.add_argument(
            "--step", type=int, default=10, help="Step"
        )
        pars.add_argument(
            "--unit", default="up", help="Direction"
        )
        pars.add_argument(
            "--port", type=str, default="com3",help="Port"
        )

    def effect(self):          
        
        # Open grbl serial port
        s = serial.Serial(str(self.options.port),115200)
        self.msg(s.readline())
        self.msg(s.readline())
        if (self.options.unit=="up"):
            encoded_string = ("y-"+str(self.options.step)+"\n").encode('utf-8')
        elif (self.options.unit=="down"):
            encoded_string = ("y"+str(self.options.step)+"\n").encode('utf-8')
        elif (self.options.unit=="left"):
            encoded_string = ("x-"+str(self.options.step)+"\n").encode('utf-8')
        else :
            encoded_string = ("x"+str(self.options.step)+"\n").encode('utf-8')
        s.write(encoded_string) # Send g-code block to grbl
        grbl_out = s.readline() # Wait for grbl response with carriage return
        self.msg(self.options.unit)

        # Open g-code file
        #f = open('gcode.nc','r');
        
        # Close file and serial port
        s.close()
		
if __name__ == '__main__':
    hello().run()
