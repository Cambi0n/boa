'''
Created on Jul 6, 2010

@author: bdf
'''

'''
Save 1 occurs after all the unit orders are given, but before the data is sent to the host.  
This is the save that each client would send for pbem.

Save 2 occurs after the host has calculated the results of the orders, but before they are carried out.
Thus in this save, the unit positions and health have not changed compared to save 1.  The only thing that is
different is that the results of orders are available.  This save would be the email that is sent from host
back to clients.

Save 3 occurs after the order resolution from host has been carried out.  This is the state of the game
at which each player can put in new orders. 

'''

import Queue
from events import *
from evmanager import *

from copy import deepcopy
from internalconstants import *
import os
import boautils as boaut

def savehero(hero,profile):
    ppath = os.path.join(profilespath, profile)
    pwn = os.path.join(ppath,hero.name)
    boaut.saveclasstodisk(hero,pwn)
    
def loadhero(profdir, herofilename):
    h = os.path.join(profdir, herofilename)
    return boaut.loadclassfromdisk(h)

class GameSave():
    def __init__(self, game):
        
#        self.viewlevelChanges = {}
        self.tiles_within_party_normal_view = {}
        self.tiles_within_party_dim_view = {}
#        self.citydict = []
#        self.unitgroups = {}
        self.objectIdDict = {}
        self.nextid = 0
        self.myprofname = None
        self.Time = 0.
        self.tot_num_pulses = 0.
        
        self.stores = []
        self.chars = []
        self.charnamesid = {}
        self.encounters = {}
        self.map_data = {}
#        self.map = {}
        
#        self.chardata = {}
#        for char in game.chars:
#            self.chardata[char.name]['orders'] = []
        
#        self.mynation = None
#        self.myteam = None
#
#        self.nation = {}
#        
#        for nn in game.nations:
#            self.nation[nn] = {}
#
#            self.nation[nn]['units'] = []
#            self.nation[nn]['movableObjects'] = []
#            self.nation[nn]['movementgroups'] = []
#            self.nation[nn]['citylist'] = []
#            self.nation[nn]['nationorderslist'] = []
#            self.nation[nn]['unitorderslist'] = []
#            self.nation[nn]['money'] = 0
        

class SaveLoad():
    def __init__(self, evManager, game):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
        
        self.game = game
        
        self.currentstate = None

    def doDeepcopySave(self, savename):     # creates a copy of game in a new memory location, 
                                            # and assigns thissave to that location
        
        thissave = self.game.saves[savename]
        
#        thissave.viewlevelChanges = deepcopy(self.game.viewlevelChanges)
        thissave.tiles_within_party_normal_view = deepcopy(self.game.tiles_within_party_normal_view)
        thissave.tiles_within_party_dim_view = deepcopy(self.game.tiles_within_party_dim_view)
        thissave.objectIdDict = deepcopy(self.game.objectIdDict)
        thissave.nextid = self.game.nextid
        thissave.Time = self.game.Time
        thissave.myprofname = self.game.myprofname
        thissave.tot_num_pulses = self.game.tot_num_pulses

        thissave.stores = deepcopy(self.game.stores)
        thissave.chars = deepcopy(self.game.chars)
        thissave.charnamesid = deepcopy(self.game.charnamesid)
        thissave.encounters = deepcopy(self.game.encounters)
        thissave.map_data = deepcopy(self.game.map_data)
#        thissave.map = deepcopy(self.game.map)
        
    def doSave(self, savename):     # assigns thissave to the existing game memory location
        
        self.currentstate = savename
        
        thissave = self.game.saves[savename]
        
#        thissave.viewlevelChanges = self.game.viewlevelChanges
        thissave.tiles_within_party_normal_view = self.game.tiles_within_party_normal_view
        thissave.tiles_within_party_dim_view = self.game.tiles_within_party_dim_view
#        thissave.citydict = self.game.citydict
#        thissave.unitgroups = self.game.unitgroups
        thissave.objectIdDict = self.game.objectIdDict
        thissave.nextid = self.game.nextid
        thissave.Time = self.game.Time
        thissave.myprofname = self.game.myprofname
        thissave.tot_num_pulses = self.game.tot_num_pulses
        
        thissave.stores = self.game.stores
        thissave.chars = self.game.chars
        thissave.charnamesid = self.game.charnamesid
        thissave.encounters = self.game.encounters
        thissave.map_data = self.game.map_data
#        thissave.map = self.game.map

    def restoreDeepcopySave(self, savename):    # creates a copy of thissave in a new memory location
                                                # and assigns game to this new location
        
        thissave = self.game.saves[savename]
        
#        self.game.viewlevelChanges = deepcopy(thissave.viewlevelChanges)
        self.game.tiles_within_party_normal_view = deepcopy(thissave.tiles_within_party_normal_view)
        self.game.tiles_within_party_dim_view = deepcopy(thissave.tiles_within_party_dim_view)
        self.game.citydict = deepcopy(thissave.citydict)
#        self.game.unitgroups = deepcopy(thissave.unitgroups)
        self.game.objectIdDict = deepcopy(thissave.objectIdDict)
        self.game.nextid = thissave.nextid
            
        for natname in self.game.nations:
            nation = self.game.Nations[natname]
            
            nation.units = deepcopy(thissave.nation[natname]['units'])
            nation.movableObjects = deepcopy(thissave.nation[natname]['movableObjects'])
            nation.movementgroups = deepcopy(thissave.nation[natname]['movementgroups'])
            nation.citylist = deepcopy(thissave.nation[natname]['citylist'])
            nation.orderslist = deepcopy(thissave.nation[natname]['orderslist'])
            nation.unitorderslist = deepcopy(thissave.nation[natname]['unitorderslist'])
            nation.money = thissave.nation[natname]['money']
            
    def restoreSave(self, savename):        # assigns game's memory location to the memory location of thissave
        
        thissave = self.game.saves[savename]
        
#        self.game.viewlevelChanges = thissave.viewlevelChanges
        self.game.tiles_within_party_normal_view = thissave.tiles_within_party_normal_view
        self.game.tiles_within_party_dim_view = thissave.tiles_within_party_dim_view
#        self.game.citydict = thissave.citydict
#        self.game.unitgroups = thissave.unitgroups
        self.game.objectIdDict = thissave.objectIdDict
        
        tempid = self.game.nextid
        self.game.nextid = thissave.nextid
        self.game.saves[self.currentstate].nextid = tempid
        
        tempnum = self.game.Time
        self.game.Time = thissave.Time
        self.game.saves[self.currentstate].Time = tempnum
        
        self.game.myprofname = thissave.myprofname
        self.game.tot_num_pulses = thissave.tot_num_pulses
        
        self.game.stores = thissave.stores
        self.game.chars = thissave.chars
        self.game.charnamesid = thissave.charnamesid
        self.game.encounters = thissave.encounters
        self.game.map_data = thissave.map_data
#        self.game.map = thissave.map
        
        self.currentstate = savename
    
    def preMovieSave(self):
        
        for natname in self.game.nations:
            nation = self.game.Nations[natname]
            
            nation.premoviesave_units = deepcopy(nation.units)
            nation.premoviesave_movableObjects = deepcopy(nation.movableObjects)
            nation.premoviesave_citylist = deepcopy(nation.citylist)
            nation.premoviesave_orderslist = deepcopy( nation.orderslist )
            nation.premoviesave_unitorderslist = deepcopy( nation.unitorderslist )
    
            nation.premoviesave_money = nation.money
            
            
        self.game.premoviesave_viewlevelChanges = deepcopy(self.game.viewlevelChanges)
        self.game.premoviesave_tiles_within_party_normal_view = deepcopy(self.game.tiles_within_party_normal_view)
        self.game.premoviesave_citydict = deepcopy(self.game.citydict)
        self.game.premoviesave_unitgroups = deepcopy(self.game.unitgroups)
        self.game.premoviesave_objectIdDict = deepcopy(self.game.objectIdDict)
        #self.game.premoviesave.tempIdDict = deepcopy(self.game.tempIdDict)
        
        self.game.premoviesave_nextid = self.game.nextid

    def restoreToPreMovieSave(self):
        
#        for natname in self.game.nations:
#            nation = self.game.Nations[natname]
#            
#            nation.units = nation.premoviesave_units
#            nation.movableObjects = nation.premoviesave_movableObjects
#            nation.citylist = nation.premoviesave_citylist
#            nation.orderslist = nation.premoviesave_orderslist
#            nation.unitorderslist = nation.premoviesave_unitorderslist
#    
#            nation.money = nation.premoviesave_money
#            
#            
#        self.game.viewlevelChanges = self.game.premoviesave_viewlevelChanges
#        self.game.tilesWithinView = self.game.premoviesave_tilesWithinView
#        self.game.citydict = self.game.premoviesave_citydict
#        self.game.unitgroups = self.game.premoviesave_unitgroups
#        self.game.objectIdDict = self.game.premoviesave_objectIdDict
#        #self.game.premoviesave.tempIdDict = deepcopy(self.game.tempIdDict)
#        
#        self.game.nextid = self.game.premoviesave_nextid

        for natname in self.game.nations:
            nation = self.game.Nations[natname]
            
            nation.units = deepcopy(nation.premoviesave_units)
            nation.movableObjects = deepcopy(nation.premoviesave_movableObjects)
            nation.citylist = deepcopy(nation.premoviesave_citylist)
            nation.orderslist = deepcopy(nation.premoviesave_orderslist)
            nation.unitorderslist = deepcopy(nation.premoviesave_unitorderslist)
    
            nation.money = nation.premoviesave_money
            
            
        self.game.viewlevelChanges = deepcopy(self.game.premoviesave_viewlevelChanges)
        self.game.tiles_within_party_normal_view = deepcopy(self.game.premoviesave_tilesWithinView)
        self.game.citydict = deepcopy(self.game.premoviesave_citydict)
        self.game.unitgroups = deepcopy(self.game.premoviesave_unitgroups)
        self.game.objectIdDict = deepcopy(self.game.premoviesave_objectIdDict)
        #self.game.premoviesave.tempIdDict = deepcopy(self.game.tempIdDict)
        
        self.game.nextid = self.game.premoviesave_nextid
            
    def postMovieSave(self):
        
        for natname in self.game.nations:
            nation = self.game.Nations[natname]
            
            nation.postmoviesave_units = deepcopy(nation.units)
            nation.postmoviesave_movableObjects = deepcopy(nation.movableObjects)
            nation.postmoviesave_citylist = deepcopy(nation.citylist)
            nation.postmoviesave_orderslist = deepcopy( nation.orderslist )
            nation.postmoviesave_unitorderslist = deepcopy( nation.unitorderslist )
    
            nation.postmoviesave_money = nation.money
            
            
        self.game.postmoviesave_viewlevelChanges = deepcopy(self.game.viewlevelChanges)
        self.game.postmoviesave_tilesWithinView = deepcopy(self.game.tiles_within_party_normal_view)
        self.game.postmoviesave_citydict = deepcopy(self.game.citydict)
        self.game.postmoviesave_unitgroups = deepcopy(self.game.unitgroups)
        self.game.postmoviesave_objectIdDict = deepcopy(self.game.objectIdDict)
        #self.game.postmoviesave.tempIdDict = deepcopy(self.game.tempIdDict)
        
        self.game.postmoviesave_nextid = self.game.nextid

    def restoreToPostMovieSave(self):
        
#        for natname in self.game.nations:
#            nation = self.game.Nations[natname]
#            
#            nation.units = nation.postmoviesave_units
#            nation.movableObjects = nation.postmoviesave_movableObjects
#            nation.citylist = nation.postmoviesave_citylist
#            nation.orderslist = nation.postmoviesave_orderslist
#            nation.unitorderslist = nation.postmoviesave_unitorderslist
#    
#            nation.money = nation.postmoviesave_money
#            
#            
#        self.game.viewlevelChanges = self.game.postmoviesave_viewlevelChanges
#        self.game.tilesWithinView = self.game.postmoviesave_tilesWithinView
#        self.game.citydict = self.game.postmoviesave_citydict
#        self.game.unitgroups = self.game.postmoviesave_unitgroups
#        self.game.objectIdDict = self.game.postmoviesave_objectIdDict
#        #self.game.postmoviesave.tempIdDict = deepcopy(self.game.tempIdDict)
#        
#        self.game.nextid = self.game.postmoviesave_nextid

        for natname in self.game.nations:
            nation = self.game.Nations[natname]
            
            nation.units = deepcopy(nation.postmoviesave_units)
            nation.movableObjects = deepcopy(nation.postmoviesave_movableObjects)
            nation.citylist = deepcopy(nation.postmoviesave_citylist)
            nation.orderslist = deepcopy(nation.postmoviesave_orderslist)
            nation.unitorderslist = deepcopy(nation.postmoviesave_unitorderslist)
    
            nation.money = nation.postmoviesave_money
            
            
        self.game.viewlevelChanges = deepcopy(self.game.postmoviesave_viewlevelChanges)
        self.game.tiles_within_party_normal_view = deepcopy(self.game.postmoviesave_tilesWithinView)
        self.game.citydict = deepcopy(self.game.postmoviesave_citydict)
        self.game.unitgroups = deepcopy(self.game.postmoviesave_unitgroups)
        self.game.objectIdDict = deepcopy(self.game.postmoviesave_objectIdDict)
        #self.game.postmoviesave.tempIdDict = deepcopy(self.game.tempIdDict)
        
        self.game.nextid = self.game.postmoviesave_nextid
                    
    def Notify(self, event):

        if isinstance( event, PreMovieSaveEvent ):
            self.preMovieSave()
            
        elif isinstance( event, PostMovieSaveEvent ):
            self.postMovieSave()
            
        elif isinstance( event, RestoreToPostMovieEvent ):
            self.restoreToPostMovieSave()
            
            

