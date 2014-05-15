#!/usr/bin/env python
from driver import *
from reader import *
from optimize import *
from sys import argv, stdout

print "Reading input...",
stdout.flush()
indata=open(argv[1]).readlines()
print "done."

print "Generating bidirectional path...",
stdout.flush()
V=bidir_from_ascii(indata)
print "done."

print "Calculating distance matrix...",
stdout.flush()
dm=distance_matrix(V, cost)
print "done."

print "Calculating sorted shortest distance matrix...",
stdout.flush()
sd=shortest_distances(dm)
print "done."

greedy=greedy_fill(sd)

l=len(V)
bidir=range(l)
print "Bidirectional:", l, path_cost(dm, bidir)
print "Greedy:", l, path_cost(dm, greedy)

print "Optimize bidir"
local_opt_maxfirst(dm, bidir, 7)
print "Optimize greedy"
local_opt_maxfirst(dm, greedy, 7)

bidir_cost=path_cost(dm, bidir)
greedy_cost=path_cost(dm, greedy)
print "Bidirectional:", l, bidir_cost
print "Greedy:", l, greedy_cost

ps=(max(V, 0)+1)[1::-1]
print "Print size:", ps
printer=SimulatedPrinter(*ps)
path=greedy
if bidir_cost<greedy_cost:
    path=bidir

sel=raw_input("sel?")
if sel=="greedy":
    path=greedy
elif sel=="bidir":
    path=bidir
    
pt=PrintingThread(printer, V[path])
pt.start()
while pt.isAlive():
    from time import sleep
    sleep(.1)

