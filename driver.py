from scipy import array
from time import sleep

# typewriter pos:
# [feed, carriage, wheel]
# costs for moving each f,c,w one unit
feed, carriage, wheel=range(3)

# type alphabet (non printable chars will be ignored)
wheeltypes=",.ersaioctmlhpnbfgukvdyzqxjw/%1324567809${|}#>~<\0127\0128\0129@!]^[`R'Q_OJG?D\"C-FE=BV&YATLSPZ*X+K)H(UIN;W:M"

# number of types
ntypes=len(wheeltypes)

cost=[90, 36, 4] # for each feed, carriage, wheel movement

class SimulatedPrinter:
    def __init__(self, X=78, Y=30):
        self.X, self.Y=X, Y
        self.zero()
        
    def do(self, action):
        f, c, w=action
        char=wheeltypes[w]
        self.sheet[f][c]=char

        print "%3d %3d %3d %c" % (f, c, w, char)
        for l in self.sheet:
            print l
        print
        sleep(.05)

    def zero(self):
        self.sheet=[bytearray(" "*self.X) for i in range(self.Y)]
        
class AMTWriter:
    def __init__(self, port="/dev/ttyACM0", reset=True):
        # number of steps for one char movement
        # each axis
        # feed, carriage, wheel
        self.step_multipliers=[-30,12,2]

        self.pos=array([0,0,0], int)

        from serial import Serial
        self.ser=Serial(port, 115200, timeout=30)
        self.ser.flushInput()
        if reset:
            self.reset()
        self.zero()
            

        
    def zero(self):
        self.do([self.pos[feed],
                 0,
                 self.pos[wheel]], False)
        self.pos=array([0,0,0], int)
                
    def reset(self):
        self.exchange("r")
        
    def status(self):
        self.ser.write("x")
        status=self.ser.readline()[:-3]
        #print "status", repr(status)
        return [int(s) for s in status.split()]

    def exchange(self, msg):
        #print "->", repr(msg)
        self.ser.write(str(msg))
            
        resp=self.ser.readline()
        #print "response", repr(resp)
        assert resp == ".\r\n"

    def set_steps(self, n):
        self.exchange("0")
        n-=1

        for i, r in enumerate([1000, 100, 10, 1]):
            while n>=r:
                self.exchange("8765"[i])
                n-=r
        
    def do(self, action, strike=True):
        from scipy import int16
        delta=array(action-self.pos, int16)

        delta*=self.step_multipliers
        
        # if delta[wheel]>ntypes/2:
        #     delta[wheel]=-self.step_multipliers[wheel]*ntypes+delta[wheel]
        # if delta[wheel]<-ntypes/2:
        #     delta[wheel]=self.step_multipliers[wheel]*ntypes+delta[wheel]

        #print delta
        cmd=bytearray("a\x00\x00\x00\x00\x00\x00")
        if strike:
            cmd[0]='A'
        cmd[1:3]=delta[    feed] & 0xff, (delta[      feed] &0xff00)>>8
        cmd[3:5]=delta[carriage] & 0xff, (delta[  carriage] &0xff00)>>8
        cmd[5:7]=delta[   wheel] & 0xff, (delta[     wheel] &0xff00)>>8
        self.exchange(cmd)
        self.pos=array(action, int)

    def do_(self, action, strike=True):
        self.do_([action[0],   self.pos[1], self.pos[2]], False)
        self.do_([self.pos[0], action[1],   self.pos[2]], False)
        self.do_([self.pos[0], self.pos[1], action[2]  ], True)

from threading import Thread, RLock

class PrintingThread(Thread):
    def __init__(self, printer, cmds):
        self.cmds=cmds
        self.printer=printer
        self.lock=RLock()
        self.state=0
        Thread.__init__(self)
        
    def run(self):
        printer=self.printer
        printer.zero()
        for i, step in enumerate(self.cmds):
            printer.do(step)
            self.lock.acquire()
            self.state=i
            self.lock.release()
            
    def progress(self):
        self.lock.acquire()
        res=self.state
        self.lock.release()
        return res/float(len(self.cmds)-1)
        
