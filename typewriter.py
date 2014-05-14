#!/usr/bin/env python
from scipy import random, array
from scipy import random
randint=random.randint

cost=[1, 1, 1] # for each feed, carriage, wheel movement

from driver import *
printer=SimulatedPrinter()

def bidir_from_ascii(lines, printer):
    """ Create bidirectional printer path from a set of ASCII lines.
    Use open("filename").readlines() or similar as input. """
    res=[]
    # create simple direct bidirectional path from ASCII
    for i, line in enumerate(lines):
        if i%2:
            r=range(len(line)-1, -1, -1)
        else:
            r=range(len(line))
            
        for j in r:
            ch=line[j]
            if ch in printer.wheeltypes:
                res.append([i, j, printer.wheeltypes.index(ch)])
    return res


def greedy_fill(path, cost=cost):
    """ Take a path and starting with path[0], go to the nearest
    neighbors in a greedy fashion.
    TODO/FIXME: Uses euclidean distance instead of manhattan distance. """
    from scipy.spatial import cKDTree
    print "cost", cost
    tree=cKDTree(array(path, int)*cost)
    sel=[]
    done=set()
    pos=path[0]
    while len(sel)<len(path):
        query=True
        n=1
        while query:
            n*=2
            q=tree.query(pos, n)[1]
            #print len(sel), len(path), n, q, sel
            for l in q[n/2-1:]:
                if l not in done:
                    sel.append(l)
                    done.add(l)
                    pos=path[l]
                    query=False
                    break

    return [path[s] for s in sel]
    
current=[0,0,0]

def path_cost(path):
    pos=current
    c=0
    for step in path:
        for axis in range(3):
            if axis==wheel:
                # wrap around handling for wheel
                d=abs(pos[wheel]-step[wheel])
                if d<=printer.ntypes/2:
                    c+=cost[axis]*d
                else:
                    c+=cost[axis]*(printer.ntypes-d)
            else:
                c+=cost[axis]*abs(pos[axis]-step[axis])
        pos=step
    return c
    
def swap_random(path):
    i=randint(0, len(path))
    j=randint(0, len(path))
    tmp=path[i]
    path[i]=path[j]
    path[j]=tmp

def swap_adjacent(path):
    i=randint(0, len(path)-1)
    tmp=path[i]
    path[i]=path[i+1]
    path[i+1]=tmp
    
def reverse_section(path):
    i=randint(0, len(path)-1)
    j=randint(i+1, len(path))
    tmp=path[i:j]
    tmp.reverse()
    path[i:j]=tmp

def swap_sections(path):
    lp=len(path)
    l=randint(1, lp/2+1)
    a=randint(0, lp-2*l+1)
    b=a+l
    c=randint(b, lp-l+1)
    d=c+l

    # print lp, l, a, b, c, d
    # assert a<b
    # assert c<d
    # assert b<=len(path)
    # assert d<=len(path) 
    # assert (b-a) == (d-c)
    
    tmp=path[a:b]
    path[a:b]=path[c:d]
    path[c:d]=tmp

if 0:
    indata=[
        "aaa   bbb",
        "aaa   bbb"
    ]

if 1:
    indata=open("scott.txt").readlines()


    
path=bidir_from_ascii(indata, printer)

def mutate(path):
    if random.random()<.05:
        swap_sections(path)
    else:
        reverse_section(path)


def do_print(printer, path):
    for step in path:
        printer.do(step)
        
print "Initial:", path_cost(path)
path=greedy_fill(path)
print "After greedy fill:", path_cost(path)

path=array(path, int)

if 0:
    from anneal import Annealer
    #annealer = Annealer(path_cost, path_mutate)
    annealer = Annealer(path_cost, swap_adjacent)
    schedule = annealer.auto(path, minutes=1.0)
    path, e = annealer.anneal(path, schedule['tmax'], schedule['tmin'], 
                                schedule['steps'], updates=6)
    #print state  # the "final" solution

raw_input()
do_print(printer, path)
