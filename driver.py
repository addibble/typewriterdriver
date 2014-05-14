# typewriter pos:
# [feed, carriage, wheel]
# costs for moving each f,c,w one unit
feed, carriage, wheel=range(3)

class SimulatedPrinter:
    def __init__(self):
        # type alphabet (non printable chars will be ignored)
        self.wheeltypes="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890.,:'"

        # number of types
        self.ntypes=len(self.wheeltypes)

        self.sheet=[bytearray(" "*80) for i in range(80)]

    def do(self, action):
        print action
        f, c, w=action
        char=self.wheeltypes[w]
        self.sheet[f][c]=char

        print f, c, w, char
        for l in self.sheet:
            print l
        print
        from time import sleep
        sleep(.001)


class AMTWriter:
    def __init__(self):
        from serial import Serial
        self.ser=Serial("/dev/ttyACM0", 9600, timeout=10)
        self.ser.flushInput()
        self.reset()
        # type alphabet (non printable chars will be ignored)
        self.wheeltypes=".ersaioctmlhpnbfgukvdyzqxjw/%1324567809$   #> <   @!] [ R'Q_OJG?D\"C-FE=BV&YATLSPZ*X+K)H(UIN;W:M,"

        # number of types
        self.ntypes=len(self.wheeltypes)


        # number of steps for one char movement
        # each axis
        # feed, carriage, wheel
        self.step_multipliers=[1,1,2]
        
        
    def reset(self):
        self.exchange("r")
        from scipy import array
        self.pos=array([0,0,0], int)
        
    def status(self):
        self.ser.write("x")
        status=self.ser.readline()[:-1]
        return [int(s) for s in status.split()]

    def exchange(self, msg):
        for ch in msg:
            self.ser.write(ch)
            resp=self.ser.readline()
            assert resp == "."

    def set_steps(n):
        self.exchange("0")
        n-=1

        for i, r in enumerate([1000, 100, 10, 1]):
            while n>r:
                self.xchange("8765"[i])
                n-=r
        
    def do(self, action):
        delta=action-self.pos

        delta*=self.step_multipliers

        df, dc, dw=delta

        for axis in range(3):
            d=delta[axis]
            if d:
                cmd="jkhl[]"[axis*2+(d>0)]
                self.set_steps(axis, d)
                self.exchange(cmd)

        self.exchange("s")
        
        
