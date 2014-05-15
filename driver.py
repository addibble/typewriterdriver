from time import sleep

# typewriter pos:
# [feed, carriage, wheel]
# costs for moving each f,c,w one unit
feed, carriage, wheel=range(3)

# type alphabet (non printable chars will be ignored)
wheeltypes=",.ersaioctmlhpnbfgukvdyzqxjw/%1324567809$   #> <   @!] [ R'Q_OJG?D\"C-FE=BV&YATLSPZ*X+K)H(UIN;W:M"

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
        if port!=None:
            from serial import Serial
            self.ser=Serial(port, 115200, timeout=10)
            self.ser.flushInput()
            if reset:
                self.reset()
            self.zero()
            
        from scipy import array
        self.pos=array([0,0,0], int)



        # number of steps for one char movement
        # each axis
        # feed, carriage, wheel
        self.step_multipliers=[30,12,2]
        
    def zero(self):
        self.do([0,0,0], False)
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
        for ch in msg:
            self.ser.write(ch)
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
        delta=action-self.pos

        delta*=self.step_multipliers

        #print delta
        
        for axis in range(3):
            d=delta[axis]

            # typewheel optimization
            if axis==9:
                if d>ntypes/2:
                    d=ntypes-d
                if d<-ntypes/2:
                    d=ntypes+d
            if d:
                cmd="kjhl[]"[axis*2+(d>0)]
                self.set_steps(abs(d))
                self.exchange(cmd)
                
        if strike:
            self.exchange("s")

        from scipy import array
        self.pos=array(action, int)


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
        
