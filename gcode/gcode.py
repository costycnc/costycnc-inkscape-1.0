import inkex,sys,math,time,ctypes,os
from inkex import bezier
from inkex.elements import Group, Line,Circle,PathElement
from datetime import datetime
from tkinter import messagebox as mb

class hello(inkex.EffectExtension):


    def add_arguments(self, pars):
        pars.add_argument(
            "--feedrate", type=int, default=500, help="Feedrate"
        )
        pars.add_argument(
            "--temperature", type=int, default=1000, help="Temperature "
        )

    def effect(self):
    
    

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
            g +="G01 X"+"{:.2f}".format(gc[0])+" Y"+"{:.2f}".format(gc[1])+"\n"
            
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
	    

		
if __name__ == '__main__':
    hello().run()
