#!/usr/bin/env python
import logging
logging.basicConfig(filename="typewriter.log",
                    format="%(asctime)-15s %(message)s",
                    level=logging.INFO)

from config import *

from time import sleep, time, asctime
import glob
from driver import *
import reader
from optimize import *
from os import system

class PrintJob:
    def __init__(self, fn, prio):
        self.fn=fn
        logging.info("New print job %d" % prio)
        logging.info("Reading input '%s'" % fn)
        self.date=asctime()
        self.prio=prio
        self.indata=open(fn).readlines()
        logging.info("done.")
        self.V=reader.bidir_from_ascii(self.indata)
        if not len(self.V):
            self.scrap=True
            return
        self.l=len(self.V)
        self.path=range(self.l)
        self.ps=(max(self.V, 0)+1)[1::-1]
        logging.info("Print size %s" % self.ps)
        self.opt=None
        self.scrap=False
                
    def __cmp__(self, other):
        return self.prio.__cmp__(other.prio)
        
if __name__=="__main__":
    if sim:
        printer=None # will be remade for every print
    else:
        try:
            printer=AMTWriter("/dev/ttyACM0")
        except IOError:
            try:
                printer=AMTWriter("/dev/ttyACM1")
            except IOError:
                printer=AMTWriter("/dev/ttyACM2")

    N=0 # job id
    queue=[]
    pt=None # printing thread
    opt=None, None
    on=1
    
    def stats():
        #system("clear")
        print asctime()
        print "AMT WRITER STATS"
        print "----------------"
        for pj in queue:
            print "%10d %10d %s %s" % (pj.prio, pj.l, pj.fn, pj.date)
        if pt:
            print "Printing %s, %5.2f" % (queue[0].fn, 100.*pt.progress())
        print "\n"
    
    otime=time()
    
    while True:
        t=time()
        if t-otime>.5:
            otime=time()
            stats()
        newfiles=glob.glob(job_dir+"*.txt")
        if newfiles:
            logging.info("Found new job(s)")
            for fn in newfiles:
                pj=PrintJob(fn, N)
                if pj.scrap:
                    fro, to=fn, fn+".empty"
                    logging.info("Empty print job.")
                else:
                    fro, to=fn, fn+".in_queue"
                logging.info("Moving %s to %s." % (fro, to))
                system("mv %s %s" % (fro, to))
                if not pj.scrap:
                    N+=1
                    queue.append(pj)
                    on=1
            
        queue.sort() # FIXME: inefficient...

        if pt==None and len(queue):
            log.info("Printer idle, queue non-empty. Starting print.")
            to_print=queue[0]
            if sim:
                log.info("Creating new simulated printer.")
                if printer:
                    del printer
                printer=SimulatedPrinter(*to_print.ps, quiet=False,
                                         outfile=open("simulation.out",
                                                      "w"))
            pt=PrintingThread(printer, to_print.V[to_print.path])
            pt.start()

        if pt!=None:
            if not pt.isAlive():
                logging.info("Done printing current job.")
                fro, to=queue[0].fn+".in_queue", queue[0].fn+".done"
                logging.info("Moving %s to %s." % (fro, to))
                system("mv %s %s" % (fro, to))
                pt=None
                del queue[0]

        if on<len(queue):
            pj=queue[on]
            if not pj.opt and not opt[0]:
                log.info("New optimizer.")
                log.info("Optimizer cursor: %d[%d]" %
                         (on, len(queue)))
                opt=path_optimizer(pj.V, pj.path), pj
            elif opt[0]:
                try:
                    opt[0].next()
                except StopIteration:
                    log.info("Optimizer done. Advancing to next path.")
                    opt[1].opt=True
                    opt=None, 0
                    on+=1
        else:
            on=1
            
        sleep(1.)
        
from time import time
start=time()
while pt.isAlive():
    sleep(.1)
end=time()
print "duration", end-start, "s"
