from scipy import array
from driver import wheeltypes

def bidir_from_ascii(lines):
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
            if ch!=" " and ch in wheeltypes:
                res.append([i, j, wheeltypes.index(ch)])
    return array(res, int)
