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
            "--feedrate", type=int, default=500, help="Feedrate"
        )
        pars.add_argument(
            "--temperature", type=int, default=1000, help="Temperature "
        )
        pars.add_argument(
            "--dpi", type=float, default=96, help="DPI "
        )
        pars.add_argument(
            "--port", type=str, default="com4",help="Port"
        )

    def effect(self):
    
    
        dp=self.options.dpi/25.4
        a=0
        b=[]
        c=[]
        if(len(self.svg.selected)!=1):
            self.msg("Attention!!! No path or more that 1 path selected!")
            return
        csp_list = self.svg.selected[0].path.to_superpath()
        bezier.cspsubdiv(csp_list,.1) 
        
        #put coord of all path of csp_list from 3 value in paths with 1 value
        #[[968.317, 290.616], [968.317, 290.616], [957.608, 285.97]] to [968.317, 290.616]
        for csp in csp_list:                
            for cord in csp:
                a +=1
                b.append([cord[0][0],cord[0][1]])
            c.append(b)
            b=[]
        
        # c contain now all path with only one x,y coordinate

        pathx=[[0,0]]

        
        while(len(c)):
            minDiff = sys.maxsize
            for i, d in enumerate(pathx):
                for m,csp in enumerate(c): 
                    for n,cord in enumerate(csp): 
                        currDiff=math.dist(d,cord)
                        if (currDiff < minDiff):
                            minDiff = currDiff
                            pos0 = i
                            pat1 = m
                            pos1 = n
                          
            p=c.pop(pat1)
            p=p[pos1:]+p[:pos1]
            if (p[0]!=p[-1]):
                p.append(p[0])
            pathx=pathx[:pos0]+[pathx[pos0]]+p+pathx[pos0:]  

        
        g="G21 F"+str(self.options.feedrate)+" G90\nG92 X0 Y0\nM03 S"+str(self.options.temperature)+"\n"
        for gc in pathx:
            g +="G01 X"+"{:.2f}".format(gc[0]/dp)+" Y"+"{:.2f}".format(gc[1]/dp)+"\n"
            
        g +="G01 X0 Y0"
            
        dt_string = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
        
        #pathset = os.path.join(homedir, "\Documents\School Life Diary")
        
        pathset=os.path.expanduser('~/documents/costycnc/')
        
        #os.path.expanduser('~\documents\costycnc\'+dt_string+'.nc')
        
        if not(os.path.exists(pathset)):

            os.mkdir(pathset)
            
        self.msg('('+pathset+'costycnc.nc)')             
        self.msg(g)

        with open("gcode.nc", "w") as f:
            f.write(g)   
         
        with open(pathset+dt_string+'.nc', "w") as f:
            f.write(g)
            
        f.close()
	    
        # Open grbl serial port
        s = serial.Serial(str(self.options.port),115200)
        time.sleep(2)
        self.msg(s.readline())
        self.msg(s.readline())
        # Stream g-code to grbl
        f = open('gcode.nc','r');
        s.timeout = 10
        for line in f:
            #l = line.strip() # Strip all EOL characters for streaming
            #self.msg( 'Sending: ' + line)
            encoded_string = line.encode('utf-8')
            s.write(encoded_string) # Send g-code block to grbl
            grbl_out = s.readline() # Wait for grbl response with carriage return


        
        
        
        #encoded_string = "x100\n".encode('utf-8')
        #s.write(encoded_string) # Send g-code block to grbl
        #self.msg(s.readline())
 
        # Open g-code file
        #f = open('gcode.nc','r');
        
        # Close file and serial port
        f.close()

        s.close()
		
if __name__ == '__main__':
    hello().run()
