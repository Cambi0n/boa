'''
Created on May 16, 2011

@author: bdf
'''

import pygame
from pgu import gui
from userconstants import *
#from internalconstants import *
from fontdefs import *

def trimlabel(lbl, lfont, maxwidth):
    toolong = True
    testlabel = lbl
    while toolong:
        flbl = gui.Label(testlabel, font = lfont)
        if flbl.style.width > maxwidth:
            testlabel = testlabel[:-1]
        else:
            toolong = False
    return testlabel

def trimlabels(lbllist, lfont, maxwidth):
    outlist = []
    for lbl in lbllist:
        tlab = trimlabel(lbl, lfont, maxwidth)
        outlist.append(tlab)
                
    return outlist


class trimAllLabels():
    def __init__(self, view):
        self.tdict = {}
#        self.tdict['retreatdec'] = trimlabels(RetreatLabels, fontfbtr26, 130)
#        self.tdict['incombat'] = trimlabels(CombatLabels, fontfbtr26, 130)
#        self.tdict['spot'] = trimlabels(SpotLabels, fontfbtr26, 130)
        
        



