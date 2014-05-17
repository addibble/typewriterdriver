from numpy import array, zeros, sum, abs, min, max, random, uint16
import driver
from driver import *
import logging
log=logging.getLogger('optimize')

randint=random.randint
from config import *

# def edge_cost(edge0, edge1, cost):
#     diff=abs(edge1-edge0)

#     # wrap around handling for wheel
#     if diff[wheel]>ntypes/2:
#         diff[wheel]=ntypes-diff[wheel]
        
#     return sum(diff*cost)

def distance_matrix(
        V, # vertices
        cost):
    cost=array(cost)
    l=len(V)
    V=array(V, int)*cost

    res=zeros((l, l), uint16)
    for i in range(l):
        diff=abs(V-V[i])

        # wrap around
        wrap=diff[:,wheel]>(cost[2]*ntypes/2)
        diff[wrap]*=[1,1,-1]
        diff[wrap]+=[0,0,cost[2]*ntypes]

        res[i]=max(diff, 1)
    return res
    
def shortest_distances(dm):
    # indices for shortest distances for each vertex
    l=len(dm)
    res=zeros((l, l), uint16)
    r=range(l)

    def lla(l):
        return array([
            [i[0] for i in l],
            [i[1] for i in l]],
                     uint16).T
                     
    for i in r:
        a=zip(dm[i], r)
        a.sort()
        res[i]=lla(a)[:,1]
    return res
    
def path_cost(dm, path):
    c=0
    for p0, p1 in zip(path[1:], path[:-1]):
        c+=dm[p0, p1]
    return c

def greedy_fill(sd):
    l=len(sd)
    track=[]
    pos=0
    seen=set()
    while len(track)<l:
        seen.add(pos)
        track.append(pos)
        for s in sd[pos]:
            if s not in seen:
                pos=s
                break
    return track

def best_path(dm, path):
    from itertools import permutations
    best=1e99
    bestpath=None
    for p in permutations(path[1:-1]):
        par=[path[0]]+list(p)+[path[-1]]
        cost=path_cost(dm, par)
        if cost<best:
            if bestpath==None:
                oldcost=cost
            best=cost
            bestpath=par
    return bestpath, best, oldcost

def localcost(dm, path, nbors):
    # local path segment cost
    costs=[path_cost(dm, path[i:i+nbors]) for i in range(len(path)-nbors)]
    a=zip(costs, range(len(costs)))
    # highest cost stuff (with probably the most
    # possibilities of optimization) first
    a.sort(reverse=True) 
    return a

def local_opt_maxfirst(dm, path, nbors, limit=None):
    l=len(path)
    curcost=path_cost(dm, path)
    initial=curcost
    c=localcost(dm, path, nbors)
    n=0
    for cost, pos in c[:limit]:
        bestpath, best, oldcost=best_path(dm, path[pos:pos+nbors])
        path[pos:pos+nbors]=bestpath
        curcost-=oldcost-best
        if False and (n%300)==0:
            print  ("%5.2f%% %5.2f%%" %
                    (100.*n/len(c),
                    100. *float(curcost)/initial))
        n+=1
    if False:
        print  ("%5.2f%% %5.2f%%" %
                (100.*n/len(c),
                 100. *float(curcost)/initial))
    
def local_opt_random(dm, path, nbors, N=None):
    l=len(path)
    if N==None:
        N=l
    curcost=path_cost(dm, path)
    initial=curcost
    n=0
    for i in range(N):
        pos=randint(0, len(path)-nbors)
        bestpath, best, oldcost=best_path(dm, path[pos:pos+nbors])
        path[pos:pos+nbors]=bestpath
        curcost-=oldcost-best
        if False and (n%300)==0:
            print  ("%5.2f%% %5.2f%%" %
                    (100.*n/N,
                    100. *float(curcost)/initial))
        n+=1
    if False:
        print  ("%5.2f%% %5.2f%%" %
                (100.*n/N,
                 100. *float(curcost)/initial))
        


def path_optimizer(V, path):
    log.info("Starting to optimize path of length %d" % len(path))

    log.info("Calculating distance matrix")
    dm=distance_matrix(V, driver.cost)
    yield

    if fast_system:
        log.info("Calculating shortest edge matrix")
        sd=shortest_distances(dm)
        yield

        log.info("Calculating greedy path")
        greedy=greedy_fill(sd)
        log.info("Path cost bidirectional %d" % path_cost(dm, path))
        log.info("Path cost greedy %d" % path_cost(dm, greedy))
        yield

    WIDTH=6
    
    log.info("Local optimizing bidirectional with length %d" % WIDTH)
    local_opt_maxfirst(dm, path, WIDTH)
    yield

    if fast_system:
        log.info("Local optimizing greedy with length %d" % WIDTH)
        local_opt_maxfirst(dm, greedy, WIDTH)
        yield

    bidir_cost=path_cost(dm, path)
    if fast_system:
        greedy_cost=path_cost(dm, greedy)
        p=greedy
        rcost=greedy_cost
        if bidir_cost<greedy_cost:
            log.info("Selecting bidrectional path, cost %d" % bidir_cost)
            p=path
            rcost=bidir_cost
        else:
            log.info("Selecting greedy path, cost %d" % greedy_cost)
    else:
        log.info("Slow system. Selecting (optimized) bidirectional path.")
        p=path
        rcost=bidir_cost
    path[:]=p
    
