
from events import *
from internalconstants import *
import encounter_creator as ec
import os, yaml

class Town():
    def __init__(self, evManager, game):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
        self.game = game
        
    def preparetown(self, enc_module, enc_path):
        # host only

        self.enc_path = enc_path
        
        self.game.encounter_class = enc_module.Encounter()
        
        '''
Not sure if this file (enc_module) will contain anything other 
than a single class.

A 'refresh_encounter' function within the class would seem to be 
necessary, to change the map, or possibly for other reasons.
Other functions within the class that necessitate a map
change should return a variable indicating this (so main program
can call the refresh function and reset the map or choice dialog).

In order to allow switching between map-based encounters and 
choice based encounters (no map, a situation is presented and
several choices are allowed, with possibly sub-choices based on
the first choice, and then sub-sub-choices, etc.), some variable such as 
active_state = ['map', map_dir, map_file_name] or 
active_state = ['choice', choice_dir, choice_file_name] would
seem to be necessary.

The map file(s) specified will contain much of the data, such as where
players and monsters start, location of all terrain, traps, objects, etc..

The map file will also need to contain function references that are
activated upon certain events.  For example, I imagine that when
monster A is killed, that one's faction among group B (an attribute 
of this encounter class) will be changed by the function that is activated
upon the killing of monster A.  Probable categories for these function
references are: killing monster, death of monster, entering map 
location, outcome of dialog, etc.  These function references will
probably be stored in game.map_data, and then everytime something 
happens, even moving into a square, the game will need to see if there
is a special function that happens.  Results of these special functions
might have to be sent back to host and players.  Although maybe not.
Maybe there will need to be inquiry functions to return, say, the 
level of one's faction with a group.  But how will the game engine
know it needs to query?  Maybe another special function category is
to do something upon first encountering a monster, when monster first 
sees a party member.  This might lead a monster to be neutral or
friendly instead of aggressive, for example.

So how does a player check on the status of certain encounter attributes?
Maybe a list that identifies these attributes, which is fed back to the
main engine, and query functions for them.

When loading a saved encounter, the monsters will need to be placed 
based on game.map_data rather than the map file.

'''
        
        
        # todo - use the following snippet (which gives a list of attributes) 
        # in a scheme to save and load attributes when saving and loading 
        # a game in the middle of an adventure getattr(), setattr()
        # alternative is to have encounter module have save and load
        # functions
        enc_attribs = []
        for item in dir(self.game.encounter_class):
            if item[0:2] != '__':
                enc_attribs.append(item)
        
        if hasattr(self.game.encounter_class,'map_dir'):
            map_dir = self.game.encounter_class.map_dir
        else:       # map is in same dir as main encounter module
            map_dir = ''
        
        path_to_map = os.path.join(enc_path,map_dir,self.game.encounter_class.map_name)
        f = open(path_to_map, 'r')
        enc_map = yaml.load(f)
        f.close()
        
        
        stores = self.game.storefuncs.preparestores()
#        encounters = ec.prepareencs(self.game)
        self.game.saves['hostcomplete'].stores = stores        
#        self.game.saves['hostcomplete'].encounters = encounters        
        self.game.saves['hostcomplete'].encounters = enc_map        
        
        data = [stores, self.game.encounter_class.desc]
        eV = HostSendDataEvent('townprepared', data)
        queue.put(eV)
        
    def filltown(self, data):
        self.game.stores = data[0]
        self.game.encounters = data[1]
        eV = UpdateTownScreenEvent()
        queue.put(eV)
        
    def Notify(self, event):

        if isinstance( event, PrepareTownEvent ):
            self.preparetown(event.enc, event.path_to_enc)
        
        if isinstance( event, FillTownEvent ):
            self.filltown(event.data)
    