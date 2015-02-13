import threading
import os

from twisted.internet import reactor

import pygame
from pgu import gui
import pguutils as pguu

from internalconstants import *
from userconstants import *

from fontdefs import *
import boautils as boaut
import saveload as sl


class InnScreen(gui.Table):
    def __init__(self, pguctrl, **params):
        gui.Table.__init__(self, **params)
        self.pguctrl = pguctrl

        self.textstyle = {}
        self.textstyle['font'] = fontfbtr26
        self.textstyle['background'] = (30,30,140)
        self.textstyle['color'] = (200,200,200)
        
        self.labelstyle = {}
        self.labelstyle['font'] = fontfbtr26
        self.labelstyle['background'] = (25,25,130)
        self.labelstyle['color'] = (200,200,200)
        self.labelstyle['padding_left'] = 6
        self.labelstyle['padding_right'] = 6
        self.labelstyle['padding_top'] = 3
        self.labelstyle['padding_bottom'] = 3

        self.labelstyle2 = {}
        self.labelstyle2['font'] = fontfbtr26
        self.labelstyle2['background'] = (25,25,130)
        self.labelstyle2['color'] = (255,215,0)
        self.labelstyle2['padding_left'] = 6
        self.labelstyle2['padding_right'] = 6
        self.labelstyle2['padding_top'] = 3
        self.labelstyle2['padding_bottom'] = 3
        

        self.tr()
        self.shopbutton = gui.Button("Shop")
        self.shopbutton.connect(gui.CLICK, self.shop)
        self.td(self.shopbutton)
        self.shopbutton.disabled = True
        
        self.td(gui.Spacer(width = 150,height = 1))
        
        self.managecharsbutton = gui.Button("Manage Characters")
        self.managecharsbutton.connect(gui.CLICK, self.manage)
        self.td(self.managecharsbutton)
        self.managecharsbutton.disabled = True
        
        self.tr()
        self.encbutton1 = gui.Button("Blank")
        self.encbutton1.connect(gui.CLICK, self.encounter, 1)
        self.td(self.encbutton1)

        self.encbutton2 = gui.Button("Encounter")
        self.encbutton2.connect(gui.CLICK, self.encounter, 2)
        self.td(self.encbutton2)

        self.encbutton3 = gui.Button("Blank")
        self.encbutton3.connect(gui.CLICK, self.encounter, 3)
        self.td(self.encbutton3)
        
        self.tr()
        self.td(gui.Spacer(width = 150,height = 1))

        self.td(gui.Label("A Scary Dungeon", style = self.labelstyle))

        self.td(gui.Spacer(width = 150,height = 1))
        
        
    def Show(self, game):
        pgua = self.pguctrl.pguapp

        self.amihost = game.amihost
        self.ismulti = not game.singleplayer
#        self.profname = game.myprofname
        self.game = game
        
        if not self.amihost:
            self.encbutton1.disabled = True
            self.encbutton2.disabled = True
            self.encbutton3.disabled = True
            
        pgua.init(self)
        
    def manage(self):
        pass
    
    def encounter(self,idx):
        pass
    
    def shop(self):
        pass    
        

