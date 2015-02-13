#import threading
#import os

#from twisted.internet import reactor

#import pygame
from pgu import gui
import pguutils as pguu

from internalconstants import *
#from userconstants import *

from fontdefs import *
import boautils
#import saveload as sl

from events import *
import encounter_creator as ec
try:
    import cPickle as pickle
except:
    import pickle



class TownView(gui.Table):
    def __init__(self, pguctrl, **params):
        gui.Table.__init__(self, **params)
        
        self.pguctrl = pguctrl
        self.evManager = pguctrl.evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
        

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
        

        self.shopbutton = gui.Button("Shop")
        self.shopbutton.connect(gui.CLICK, self.shop)
        
        self.managecharsbutton = gui.Button("Manage Characters")
        self.managecharsbutton.connect(gui.CLICK, self.manage)

        '''
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
        '''
        
    def updateTownScreen(self):

        self.clear()
                
        self.tr()
        self.td(self.shopbutton)
        self.shopbutton.disabled = True
        
        self.td(gui.Spacer(width = 150,height = 1))
        
        self.td(self.managecharsbutton)
        self.managecharsbutton.disabled = True
        
#        numencounters = len(self.game.encounters)
#        self.tr()
#        for i in range(numencounters):
#            desc = self.game.encounters[i]
#            encbutton = gui.Button(desc)
#            encbutton.connect(gui.CLICK, self.encounter_clicked, i)
#            self.td(encbutton)

#        numencounters = len(self.game.encounters)

        self.tr()
        
        enc_desc = gui.Label(self.game.encounters, font = fontdefault22, color = (255,255,255,255))
        self.td(enc_desc)
        ready_button = gui.Button('Ready')
        ready_button.connect(gui.CLICK, self.ready_clicked)
        self.td(ready_button)
        
        if not self.game.amihost:
            ready_button.disabled = True
                
        self.pguctrl.ShowTownScreen()
            
        
    def manage(self):
        pass
    
    def ready_clicked(self):
        # only host
        
#        encounter, unified_object_ids = ec.initialize_encounter(self.game)
        encounter = ec.initialize_encounter(self.game)
        
        pickled_enc = pickle.dumps(encounter, pickle.HIGHEST_PROTOCOL)
        ev = HostSendDataEvent('fullencounterdata', pickled_enc)
        queue.put(ev)
#        ev = HostSendDataEvent('assign_imported_object_ids', unified_object_ids)
#        queue.put(ev)
        ev = HostSendDataEvent('buildmapevent')
        # received by game object *on each client*, which calls map class and 
        #    creates the map definition file.  
        # Then game sends a MapBuiltEvent, which is received by mainview,
        #    which constructs the graphical version of the map
        # mainview then sends a SwitchToEncounterModeEvent, which is received by 
        #    MasterController and does two things:
        #        changes the MasterController run loop to include UpdateViewEvent (shows the 
        #            map and other pygame things)
        #        calls pgucontrol.StartEncounter, which sets up the pgu gui abilities
        queue.put(ev)


    
    def shop(self):
        pass    
        
    def Notify(self, event):

        if isinstance( event, PassGameRefEvent ):
            self.game = event.game
            
        elif isinstance( event, UpdateTownScreenEvent ):
            self.updateTownScreen()
            

class PreTownView(gui.Table):
    # all of this is done only on host
    def __init__(self, pguctrl, **params):
        gui.Table.__init__(self, **params)
        self.pguctrl = pguctrl
        self.evManager = pguctrl.evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )

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
        
        self.mode = 'initial choice'
        self.choice_made = None
        

    def update_pretown_screen(self):

        self.clear()
        
        if self.mode == 'initial choice':
            self.show_initial_choice_screen()
        elif self.mode == 'random encounter':
            self.show_random_encounter_choices()
        elif self.mode == 'choose encounter':
            self.choose_scripted_encounter()
        elif self.mode == 'saved encounter':
            self.choose_saved_encounter()
                
        self.pguctrl.show_pre_town_screen()
        
    def show_initial_choice_screen(self):
        top_title = gui.Label('Choose either a random encounter or a script from disk', font = fontdefault22, color = (255,255,255,255))
        
        random_button = gui.Button("Random Encounter")
        random_button.connect(gui.CLICK, self.random_clicked)
        
        choose_button = gui.Button("Choose Scripted Encounter")
        choose_button.connect(gui.CLICK, self.choose_clicked)

        saved_button = gui.Button("Load Saved Encounter")
        saved_button.connect(gui.CLICK, self.saved_clicked)

        self.td(top_title, colspan = 5)
        self.tr()
        self.td(gui.Spacer(width = 1,height = 20))
        self.tr()
        self.td(random_button)
        self.td(gui.Spacer(width = 70,height = 1))
        self.td(choose_button)
        self.td(gui.Spacer(width = 70,height = 1))
        self.td(saved_button)
    
    def random_clicked(self):
        pass
#        self.mode = 'random encounter'
#        self.update_pretown_screen()
        
    def choose_clicked(self):
        self.mode = 'choose encounter'
        self.update_pretown_screen()
        
    def saved_clicked(self):
        pass
#        self.mode = 'saved encounter'
#        self.update_pretown_screen()
        
    def show_random_encounter_choices(self):
        pass
    
    def choose_scripted_encounter(self):
        d = pguu.FileDialogWithFilter()
#        d = gui.FileDialog()
        d.connect(gui.CHANGE, self.handle_file_browser_closed, d)
        self.td(d)
        
    def handle_file_browser_closed(self, dlg):
        if dlg.value:
            encounter_with_path = dlg.value 
            print 'townview2000', encounter_with_path
            enc, path_to_encounter = boautils.load_new_encounter(encounter_with_path)
            ev = PrepareTownEvent(enc, path_to_encounter)
            queue.put(ev)
#            input_file.value = dlg.value

    def choose_saved_encounter(self):
        pass
    
#    def encounter_clicked(self,idx):
#        # only host
#        
#        encounter, unified_object_ids = ec.initialize_encounter(self.game,idx)
#        
#        pickled_enc = pickle.dumps(encounter, pickle.HIGHEST_PROTOCOL)
#        ev = HostSendDataEvent('fullencounterdata', pickled_enc)
#        queue.put(ev)
#        ev = HostSendDataEvent('assign_imported_object_ids', unified_object_ids)
#        queue.put(ev)
#        ev = HostSendDataEvent('buildmapevent')
#        # received by game object *on each client*, which calls map class and 
#        #    creates the map definition file.  
#        # Then game sends a MapBuiltEvent, which is received by mainview,
#        #    which constructs the graphical version of the map
#        # mainview then sends a SwitchToEncounterModeEvent, which is received by 
#        #    MasterController and does two things:
#        #        changes the MasterController run loop to include UpdateViewEvent (shows the 
#        #            map and other pygame things)
#        #        calls pgucontrol.StartEncounter, which sets up the pgu gui abilities
#        queue.put(ev)
        
    def Notify(self, event):

        if isinstance( event, PassGameRefEvent ):
            self.game = event.game
            
#        elif isinstance( event, PrepareTownEvent ):
#            self.update_pretown_screen()
        
        elif isinstance( event, UpdatePreTownScreenEvent ):
            self.update_pretown_screen()
            

