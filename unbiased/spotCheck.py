#!/usr/bin/env python3

import sys

from unbiased.parser import *
from unbiased.unbiasedObjects import *

def spotCheck(src):

    fns = {'hil' : buildTheHill,
           'cbs' : buildCBS,
           'npr' : buildNPR,
           'fox' : buildFoxNews,
           'gdn' : buildGuardian,
           'blz' : buildBlaze,
           'bbc' : buildBBC,
           'nbc' : buildNBC,
           'wat' : buildWashTimes,
           'csm' : buildCSM,
           'abc' : buildABC}

    data=fns[src]()

    print('H1s:\n--------------')
    for h in data.h1Arr:
        print(h.title)

    print('\n\nH2s:\n--------------')
    for h in data.h2Arr:
        print(h.title)

    print('\n\nH3s:\n--------------')
    for h in data.h3Arr:
        print(h.title)

    print('\n\n')



if __name__=='__main__':
    spotCheck(sys.argv[1])
