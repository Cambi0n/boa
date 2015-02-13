#import wx
#import wx.combo
#import threading
#import Queue
import os
import yaml

import pygame
from pgu import gui

from internalconstants import *
#from events import *
#from wxcustom import *
#from wxmultistart import *
from twiststart import *
from netfunctions import *
#from userconstants import *
import pguutils as pguu
import initialpartyscreen as ips
import boautils as boaut
import adventurer as adv
from fontdefs import *
import object_utils

class FirstScreen(gui.Table):
    def __init__(self, pgua, evManager, **params):
        gui.Table.__init__(self, **params)

        self.pgua = pgua
        self.evManager = evManager
        
        self._count = 0
        self.ListProfiles()
    
        self.tr()
        
#        self.mfont = pygame.font.Font(resourcepath + 'freebooter.ttf',36)
        self.inpstyle = {}
        self.inpstyle['font'] = fontfbtr26
        self.inpstyle['color'] = (230,230,230)

        self.td(gui.Label("Profiles", style = self.inpstyle))
        
        img = gui.Image(resourcepath + "singleplayer.png")
        self.b1 = pguu.BmpButton(img, theme = 'gui2theme')
        self.b1.SetBmp(gui.Image(resourcepath + 'singleplayerhover.png'),'hover')
        self.b1.SetBmp(gui.Image(resourcepath + 'singleplayerdown.png'),'down')
        self.b1.connect(gui.CLICK, self.SinglePlayerSelect, pgua, evManager)
        self.td(self.b1)
            
        self.tr()
        self.td(self.prof_list, rowspan = 5)
        self.td(gui.Spacer(width = 1,height = 64))
        self.tr()
        
        self.tr()
        img = gui.Image(resourcepath + "multiplayerhost.png")
        self.b2 = pguu.BmpButton(img, theme = 'gui2theme')
        self.b2.SetBmp(gui.Image(resourcepath + 'multiplayerhosthover.png'),'hover')
        self.b2.SetBmp(gui.Image(resourcepath + 'multiplayerhostdown.png'),'down')
        self.b2.connect(gui.CLICK, self.MPHostStart, pgua, evManager)
        self.td(self.b2)
            
        self.tr()
        self.td(gui.Spacer(width = 1,height = 64))
        self.tr()
        
        self.tr()
        
        self.cnp = gui.Button("Create New Profile", width=150)
#        self.cnp.connect(gui.CLICK, self.CreateNewProfile)
        self.cnp.connect(gui.CLICK, self.OpenDialog)
        self.td(self.cnp)
    
        img = gui.Image(resourcepath + "multiplayerjoin.png")
        self.b3 = pguu.BmpButton(img, theme = 'gui2theme')
        self.b3.SetBmp(gui.Image(resourcepath + 'multiplayerjoinhover.png'),'hover')
        self.b3.SetBmp(gui.Image(resourcepath + 'multiplayerjoindown.png'),'down')
        self.b3.connect(gui.CLICK, self.MPJoinStart, pgua, evManager)
        self.td(self.b3)
        
        if not self.prof_list.items:
            self.DisableRightButtons()

        self.npinp = gui.Input(size = 8)
        self.npdialog = NewProfDialog(self.npinp)
        self.npdialog.connect(gui.CHANGE,self.CreateNewProfile)
        
        self.prof_list.connect(gui.CHANGE,self.SetSelectedProfile)
        pgua.init(self)    
        

    def SinglePlayerSelect(self, pgua, evManager):
        ips.InitialPartyScreen(pgua, evManager, 1, 0, self.profname, background = (20,20,80))
#        SinglePlayerScreen(pgua, evManager, background = (20,20,80))

    def StartUpTwist(self):
        twistloop = TwistLoop()
        twistloop.setDaemon(True)
        twistloop.start()
    
    def MPHostStart(self, pgua, evManager):
        self.StartUpTwist()
        ips.InitialPartyScreen(pgua, evManager, 1, 1, self.profname, background = (20,20,80))
    
    def MPJoinStart(self, pgua, evManager):
        self.StartUpTwist()
        ips.InitialPartyScreen(pgua, evManager, 0, 1, self.profname, background = (20,20,80))
        
    def ListProfiles(self):
        self.dirnames = boaut.listDirectories(profilespath)
        self.prof_list = gui.List(width=150, height=200)
        if self.dirnames:
            for prof in self.dirnames:
                self._count += 1
                self.prof_list.add(prof, value = self._count)
#            self.prof_list.group.value = 1
            self.prof_list.items[1].click()
            self.prof_list.items[1].pcls = 'down'
            
            self.SetSelectedProfile()
        
            master_object_dict = temp_build_master_object_dict()     # stores data on basic versions
                                                            # of items.
#            hero1 = adv.adventurer('Ungar2', 'warrior', 'dwarf')
#            hero1.savetodisk(self.profname)
#            hero1 = adv.adventurer('Abc2', 'warrior', 'human')
#            hero1.savetodisk(self.profname)
#            hero1 = adv.adventurer('Rand2', 'cleric', 'human')
#            hero1.savetodisk(self.profname)
#            hero1 = adv.adventurer('Xyz2', 'mage', 'human')
#            hero1.savetodisk(self.profname)
            hero1 = adv.adventurer('Xyz2', {'wizard':9}, 'human')
            items_to_add = [['backpack','equipped','storage',11],['longsword','equipped','mainhand',12], ['battleaxe','storage',None,13], \
                            ['torch','equipped','offhand',14],['holy_symbol_wooden','storage',None,15]]
            for item in items_to_add:
                new_item = object_utils.create_new_item(master_object_dict[item[0]],id = item[3])
                hero1.add_item(new_item,item[1],item[2])
                if new_item.name == 'torch':
                    new_item.is_showing_light = True
            hero1.savetodisk(self.profname)
            
            self.prof_list.items[0].click()
            self.prof_list.items[0].pcls = 'down'
            
            self.SetSelectedProfile()
        
            hero1 = adv.adventurer('Ungar', {'warrior':1}, 'dwarf')
            items_to_add = [['backpack','equipped','storage',11],['longsword','equipped','mainhand',12], ['battleaxe','storage',None,13], \
                            ['torch','equipped','offhand',14],['holy_symbol_wooden','storage',None,15]]
            for item in items_to_add:
                new_item = object_utils.create_new_item(master_object_dict[item[0]],id = item[3])
                hero1.add_item(new_item,item[1],item[2])
                if new_item.name == 'torch':
                    new_item.is_showing_light = True
            hero1.savetodisk(self.profname)

#            hero1 = adv.adventurer('Abc', 'warrior', 'human', vision_type = 'darkvision')
            hero1 = adv.adventurer('Abc', {'warrior':1}, 'human')
            items_to_add = [['backpack','equipped','storage',11],['longsword','equipped','mainhand',12], ['battleaxe','storage',None,13], \
                            ['torch','equipped','offhand',14],['holy_symbol_wooden','storage',None,15]]
            for item in items_to_add:
                new_item = object_utils.create_new_item(master_object_dict[item[0]],id = item[3])
                hero1.add_item(new_item,item[1],item[2])
                if new_item.name == 'torch':
                    new_item.is_showing_light = True
            hero1.savetodisk(self.profname)

            hero1 = adv.adventurer('Rand', {'cleric':1}, 'halfelf')
            items_to_add = [['backpack','equipped','storage',11],['longsword','equipped','mainhand',12], ['battleaxe','storage',None,13], \
                            ['torch','equipped','offhand',14],['holy_symbol_wooden','storage',None,15]]
            for item in items_to_add:
                new_item = object_utils.create_new_item(master_object_dict[item[0]],id = item[3])
                hero1.add_item(new_item,item[1],item[2])
                if new_item.name == 'torch':
                    new_item.is_showing_light = True
            hero1.savetodisk(self.profname)

#            hero1 = adv.adventurer('Xyz', 'mage', 'human', vision_type = 'lowlight')
            hero1 = adv.adventurer('Xyz', {'wizard':9}, 'human')
            items_to_add = [['backpack','equipped','storage',11],['longsword','equipped','mainhand',12], ['battleaxe','storage',None,13], \
                            ['torch','equipped','offhand',14],['holy_symbol_wooden','storage',None,15]]
            for item in items_to_add:
                new_item = object_utils.create_new_item(master_object_dict[item[0]],id = item[3])
                hero1.add_item(new_item,item[1],item[2])
                if new_item.name == 'torch':
                    new_item.is_showing_light = True
            hero1.savetodisk(self.profname)
                
   
    def OpenDialog(self):                
        self.npinp.value = ""
        self.npdialog.open()    
        self.npdialog.inpwidget.focus()
                
    def CreateNewProfile(self):
        if self.npinp.value not in self.dirnames and self.npinp.value:
            self.dirnames.append(self.npinp.value) 
            boaut.makeDirectory(profilespath,self.npinp.value)
            self._count += 1
            self.prof_list.add(self.npinp.value, value = self._count)
            self.prof_list.items[self._count-1].click()
            self.prof_list.items[self._count-1].pcls = 'down'
        if self._count >= 1:
            self.EnableRightButtons()
                
    def DisableRightButtons(self):
        self.b1.disabled = True
        self.b2.disabled = True
        self.b3.disabled = True
        #self.repaint()
        
    def EnableRightButtons(self):
        self.b1.disabled = False
        self.b2.disabled = False
        self.b3.disabled = False
        #self.repaint()
        
    def SetSelectedProfile(self):
        self.profname = self.prof_list.items[self.prof_list.value-1].widget.value
        
        
def ShowFirstScreen(evManager, pgua):
    
    FirstScreen(pgua, evManager, background = (20,20,80))
    
class NewProfDialog(gui.Dialog):
    def __init__(self, inp, **params):
        self.inpwidget = inp
        
        title = gui.Label("Create Profile")
        
        main = gui.Table()
        
        main.tr()
        main.td(gui.Label("Enter Profile Name"),colspan = 2)
        main.tr()
        main.td(self.inpwidget,colspan = 2)
        main.tr()
        
        e = gui.Button("Okay")
        e.connect(gui.CLICK,self.okay)
        main.td(e)
        ##
        
        e = gui.Button("Cancel")
        e.connect(gui.CLICK,self.cancel)
        main.td(e)
        
        
        gui.Dialog.__init__(self,title,main)
        self.connect(gui.OPEN,self.focusinp)

    def okay(self):
        self.send(gui.CHANGE)
        self.close()
        
    def cancel(self):
        self.inpwidget.value = ""
        self.close()
                
    def focusinp(self):
        self.inpwidget.focus()

def temp_build_master_object_dict():
    obj_dict = {}

    dirs_under_path = boaut.listDirectories(defaultgamepath)
    if 'objects' in dirs_under_path:
        obj_dir = os.path.join(defaultgamepath,'objects')
        obj_files = boaut.listFiles(obj_dir)
        
    for obj_file in obj_files:
        this_file_with_path = os.path.join(obj_dir,obj_file)
        f = open(this_file_with_path, 'r')
        obj_list = yaml.safe_load(f)
        f.close()
        
        for obj in obj_list:    # obj is a dict of a single object
            obj_dict[obj['name']] = obj

    return obj_dict
    