import Queue
import random
#import threading

from events import *
from evmanager import *

#import pygame
#from pygame.locals import *
#from numpy import *
from copy import deepcopy

import aidecisions as ai
from hostgamecalcs import *
from gamefunctions import *
from saveload import *
from userconstants import *
from internalconstants import *
import mobj_actions as mobact
import gobj_actions as gobact
import town as twn
import stores as stor
import encounter_creator as ec
#from units import *
#import units
#import cities as cty
import view_utils
import spell_list
import conditions
import races

#------------------------------------------------------------------------------
class Game:
    """..."""
    # constructs players and nations, then
    # does GameStartingEvent, which leads to building the map
    # then MapBuiltEvent, which leads to showing the map
    # then GameStartedEvent, which leads to placing initial units

    STATE_PREPARING = 0
    STATE_RUNNING = 1
    STATE_PAUSED = 2

    #----------------------------------------------------------------------
    def __init__(self, evManager, startdata, ismulti, amihost, profname):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )

        self.ismulti = ismulti
        self.amihost = amihost
        self.myprofname = profname

        self.startdata = startdata

        self.state = Game.STATE_PREPARING

        # a player might control multiple characters
        
        self.players = []       # list of separate profiles.  Profile = separate computer (or at least
                                # separate instance of program).
        self.chars = []         # list of character names
        self.playerschars = {}  # dictionary with profiles as key, list of char names as value
        self.charsplayer = {}     # key is char name, value is profilename 
        self.charnamesid = {}     # key is charname, value is char id
         
        self.numplayers = 0
        self.numchars = 0
        self.nextid = 1
        self.objectIdDict = {}          # key is  id, value is object
        for i in range(len(startdata['name'])):
            if startdata['name'][i] != -1:
                self.numchars += 1
                thischar = startdata['all'][i]

                thischar.id = self.nextid
                self.objectIdDict[self.nextid] = thischar   
                self.nextid += 1

                self.chars.append( thischar.name )
                thisprofname = startdata['controller'][i] 
                self.charsplayer[thischar.name] = thisprofname
                self.charnamesid[thischar.name] = thischar.id
                if thisprofname not in self.players:
                    self.numplayers += 1
                    self.players.append(thisprofname)
                    self.playerschars[thisprofname] = []
                self.playerschars[thisprofname].append(thischar.name)
                
                itemslist = thischar.list_items(listall = True)
                for item in itemslist:
                    this_id = self.giveID()
                    self.objectIdDict[this_id] = item
                    item.assign_id(this_id)   


#        self.mychars = self.playerschars[self.myprofname]

        self.mobile_obj_actions = mobact.MobjActions(self,evManager)
        self.game_obj_actions = gobact.GobjActions(self,evManager)

        self.mapmaker = Mapmaker( evManager, self )
        self.ai = ai.AIDecisions(self)
        self.hostcalcs = HostGameCalcs(self)
        self.saveandload = SaveLoad(evManager, self)
        self.town = twn.Town(evManager, self)
        self.storefuncs = stor.Stores(evManager, self)  # functions related to stores
        self.complete_dict_of_spells = spell_list.complete_dict_of_spells()
        self.dict_of_conditions = conditions.dict_of_conditions()
        self.dict_of_races = races.dict_of_races()
        self.master_object_dict = None
        
        self.stores = {}      # store contents
        self.encounters = {}  # data on encounters that can be chosen, a list
                                # only hostcomplete has all the data, clients
                                # only have description
        self.encounter = {}   # the specific encounter currently active
                                # everybody has all the data
                                
        self.encounter_class = None
        self.last_updated_encounter_time = 0.
#        self.monsters = []      # list of monster ids
        self.map_section_names = []
        self.map_data = {}      # stores many things about objects and features of map.  
                                # not terrain type, subtype, or heights, but
                                # monsters, lighting, objects, traps
        # map_data is a dictionary with keys for each map section
        # the values are another dictionary
        # each of these dictionaries has keys of  'monsters', 'light', 'objects' 
        # the values for these keys are another dictionary
        # the keys for these dictonaries are (x.y) tuples for position within the sector
        # the values for these keys vary.
#        self.viewlevelChanges = {}
#        self.tiles_within_party_normal_view = {}
#        self.tiles_within_party_dim_view = {}
        self.tiles_within_party_normal_view = set()
        self.tiles_within_party_dim_view = set()
#        self.vinfo = view_utils.init_view_info()
        view_utils.init_view_info()
        
        if turn_mode == 'we_go_they_go':
            self.num_sub_phases = 2
            self.tot_num_pulses = self.num_sub_phases*num_pulses_per_unit

        self.Time = 0   # in ms
#        char_frac = 1./self.numchars
#        self.free_move_mode_time_factor = char_frac + (1.-char_frac)*free_move_mode_time_factor 
        
        self.move_mode = 'free'   # options are 'free' and 'phased'.
                                    # 'phased' means time is accurately tracked.  Orders are given, then
                                    # host calculates results and sends back to clients.  'phased' is
                                    # generally equivalent to the time when dm says 'roll for initiative'.
                                    # In 'free' mode, each char can immediately execute actions.  
        self.new_move_mode = None
                                    
        self.standard_action_time = int(round(seconds_per_round * 1000. * num_pulses_for_standard_action / num_pulses_per_unit))
        self.move_action_time = int(round(seconds_per_round * 1000. * num_pulses_for_move_action / num_pulses_per_unit))
                            
        self.saves = {}
        
        self.saves['player'] = GameSave(self)
        self.saveandload.doSave('player')
        self.saves['movie'] = GameSave(self)
        self.saveandload.doDeepcopySave('movie')
            
        if self.amihost:
#            for prof in self.players:
#                if prof != self.myprofname:
#                    self.nextid[prof] = 0
            #self.saves['hostplayer'] = GameSave(self)
            self.saves['hostcomplete'] = GameSave(self)
            self.saveandload.doDeepcopySave('hostcomplete')
            self.saves['hostcomplete'].myprofname = False
            self.saveandload.restoreSave('player')
                
        eV = PassGameRefEvent( self )
        queue.put(eV)

    #----------------------------------------------------------------------
    def Start(self):        # is run by both host and clients

        self.state = Game.STATE_RUNNING


#        eV = ShowInnScreenEvent(self)
#        queue.put(eV)
        
        '''
        self.createUnits()
        if self.myslot == 0:
            print 'compunits'
            self.ai.createCompUnits()
#            self.createCompUnits()
        
        #for t in self.teams:
            #self.viewlevelChanges[t] = {}
            #self.tilesWithinView[t] = {}

        if self.singleplayer:
            ev = AllInitUnitsCreated()
        else:
            ev = WaitForAllClients(self.myslot, self.numclients, 'Initial Create')
        queue.put(ev)
        '''
        
        #ev = GameStartedEvent( self )
        #self.evManager.Post( ev )
        
    def giveID(self):
        self.nextid += 1
        return self.nextid-1

    def createCities(self):
        numnations = len(self.nations)
        for i in range(2*numnations):   # todo: make city density a user option
            #if self.singleplayer:
                #self.CreateCity()
            #else:
            eV = CreateCityRequest()    # only host sees this event
            queue.put(eV)

    def CreateCity(self, loc):
        newcity = cty.City(loc)
        
        print 'in game create city', threading.currentThread()

        return newcity

    def assigncities(self):
        # host runs this part
        numcities = len(self.citydict)
        randcitynumlist = range(numcities)
        citydata = []
        #print 'rcl', randcitylist
        for n in self.nations:
            chosencitynum = random.choice(randcitynumlist)
            citydata.append([n, self.citydict.keys()[chosencitynum]])
            randcitynumlist.remove(chosencitynum)
            
        for citynum in randcitynumlist:
            citydata.append([-1, self.citydict.keys()[citynum]])
            
        tempcitydict = deepcopy(self.citydict)
            
        self.saves['hostcomplete'].citydict = deepcopy(tempcitydict)
        self.saveandload.restoreSave('hostcomplete')
        self.assigncitiesfromdata(citydata, True)
        
        for cp in self.compplayers:
            aisavename = 'aiplayer' + str(cp)
            self.saves[aisavename].citydict = deepcopy(tempcitydict)
            self.saveandload.restoreSave(aisavename)
            self.assigncitiesfromdata(citydata)
            
#        self.saves['hostcomplete'].citydict = deepcopy(tempcitydict)
        self.saveandload.restoreSave('player')
        self.assigncitiesfromdata(citydata)

        return citydata

    def assigncitiesfromdata(self,citydata, forceview = False):
        for ca in citydata:
            #self.citylist[ca[0]].id = ca[2]
            if ca[0] != -1:
                chosencity = self.citydict[ca[1]]
                chosencity.nation = ca[0]
                nat = self.Nations[ca[0]]
                nat.citylist.append(ca[1])
                chosencity.team = nat.team
                adjustViewLevels(chosencity,self, forceadjust = forceview)
                
    def createUnits(self):
        # put in ability to choose units here
        # will bring up unit purchase screen, while showing map
        # will allow user to place purchased units on map
        # for now, assign units to nations and assign unit locations

        '''if self.singleplayer:
            #self.numplayers = 1
            team = self.myteam
          nation = self.mynation
          startcity = self.Nations[nation].citylist[0]
            startloc = startcity.pos

            # todo, fix this since it will sometimes put units off map
          randloc = (startloc[0] + random.randint(-50,50), startloc[1] + random.randint(-50,50))
          newunit = Unit(nation, team, 'Infantry', randloc)
           newunit.uid = id(newunit)
           self.Nations[nation].units.append(newunit)

          randloc = (startloc[0] + random.randint(-50,50), startloc[1] + random.randint(-50,50))
          newunit = Unit(nation, team, 'Armor', randloc)
          newunit.uid = id(newunit)
           self.Nations[nation].units.append(newunit)
      else:'''
        #eV = CreateUnitRequest( 'Infantry', (0+200*(self.myteam+1), 100) )
        '''eV = CreateUnitRequest( 'Infantry' )
        #self.evManager.Post( eV )
        queue.put(eV)
        #ev = CreateUnitRequest( 'Armor', (100+200*(self.myteam+1), 100) )
        ev = CreateUnitRequest( 'Armor' )
        #self.evManager.Post( ev )
        queue.put(ev)
        eV = CreateUnitRequest( 'Infantry' )
        queue.put(eV)
        eV = CreateUnitRequest( 'Infantry' )
        queue.put(eV)
        eV = CreateUnitRequest( 'Infantry' )
        queue.put(eV)
        '''
        self.createUnit('Infantry',self.mynation)
        self.createUnit('Armor',self.mynation)
        self.createUnit('Infantry',self.mynation)
        self.createUnit('Infantry',self.mynation)
#        self.createUnit('Infantry',self.mynation)
        self.createUnit('Armor',self.mynation)
        self.createUnit('Armor',self.mynation)
#        self.createUnit('Armor',self.mynation)
#        self.createUnit('Armor',self.mynation)
#        self.createUnit('Armor',self.mynation)
#        self.createUnit('Armor',self.mynation)
#        self.createUnit('Armor',self.mynation)



#      ev = WaitTillAllUnitsCreated(self.myslot, self.numplayers)
#     self.evManager.Post( ev )


   #def placeUnits(self):

      #self.cnf.CreateUnitRequest( 'Infantry', (0+200*self.myteam, 100) )
     #self.cnf.CreateUnitRequest( 'Armor', (100+200*self.myteam, 100) )

      #MyNation = self.Nations[self.mynation]
##
##     MyNation.units.append(Unit(self.evManager, self.mynation, MyNation.team, 'Infantry'))
##     MyNation.units.append(Unit(self.evManager, self.mynation, MyNation.team, 'Armor'))
      #print 'GUGUGUGUGU', MyNation.units
     #for u in MyNation.units:
       #   ev = UnitPlaceEvent(u)
          #self.evManager.Post( ev )

      #for n in self.nations:
     #   if n != self.mynation:
          #   OtherN = self.Nations[n]
                #for u in OtherN.units:
             #   ev = UnitPlaceEvent(u)
                  #self.evManager.Post( ev )


    def createUnit(self, type, nationname, pos = None):
        # return info needed by clients and host
        nation = self.Nations[nationname]
        #team = nation.team
        if pos == None:
            startcityid = nation.citylist[0]
            startcity = self.citydict[startcityid]
            startloc = startcity.pos
        else:
            startloc = pos

        if nation.money - 100 >= 0:  # todo: put in unit type costs
            newunit = units.Unit(nationname, type, startloc, self)
            #newunit.id = (nationname, self.giveID())
            #self.objectIdDict[newunit.id] = newunit
            newunit.setPosition(startloc)
            #nation.units.append(newunit.id)
            #nation.movableObjects.append(newunit.id)
            nation.money -= 100
#            if self.myslot != 0 and not self.singleplayer:
            orddata = []
            orddata.append('create unit')
            orddata.append(type)
            orddata.append(startloc)
            orddata.append(newunit.id)
            nation.nationorderslist.append(orddata)
            print 'in create unit', newunit.id
            print 'in game, create unit, checking saves', id(nation.nationorderslist), id(self.saves['player'].nation[1]['nationorderslist'])
#            print 'in create unit, checking saves', self.saves['player'].nation[1]['nationorderslist']
#            print 'in create unit, checking saves', self.saves['movie'].nation[1]['nationorderslist']
            return newunit

        else:
            print 'not enough funds'    # todo: change this to an in-game message
            return None

    def assign_imported_object_ids(self, unified_ids):
        
#        if not self.amihost:        
            # note that currently both the 'hostcomplete' save and the 'player' save will
            # have the same copy of the item.  At this point, this seems ok.
            # This occurs partly because I'm choosing to store the actual 
            # item (not just the id) with the character save 
            # I don't think the above is true.  I think there are
            # 2 separate copies of each item, one in hostcomplete, equivalent one 
            # in player - bdf 2/28/12            
        for idx,pcharname in enumerate(self.chars):
            profile = self.charsplayer[pcharname]
            pcharid = self.charnamesid[pcharname]
            pchar = self.objectIdDict[pcharid]
            itemslist = pchar.list_items(listall = True)
            for item in itemslist:
                old_id = item.id
                if (profile,pcharname,old_id) in unified_ids:
                    new_id = unified_ids[(profile,pcharname,old_id)]
                    item.assign_id(new_id)
                    self.objectIdDict[new_id] = item
                    print 'game, item id', pcharname, item.name, item.id
                    
                elif (profile,pcharname,old_id,item.name,item.type[0],item.weight) in unified_ids:
                    new_id = unified_ids[(profile,pcharname,old_id,item.name,item.type,item.weight)]
                    item.assign_id(new_id)
                    self.objectIdDict[new_id] = item
                else:
                    print 'problem assigning id to imported item ', profile, pcharname, item.name
                        
                    
    def set_all_lighting(self,light_data):
        for section_name in self.map_section_names:
            self.set_all_lighting_for_map_section(light_data[section_name], section_name)
#            self.map_data[section_name]['light'] = light_data[section_name]
            
    def set_all_lighting_for_map_section(self, section_light_data, section_name):
        self.map_data[section_name]['light'] = section_light_data

    def set_map_section_names(self):            
        for map_section in self.encounter['sections']:
            self.map_section_names.append(map_section['name'])
            
#    def change_view_levels(self, view_set_changes):
#        for map_section_name in view_set_changes.iterkeys():
#            self.viewlevelChanges[map_section_name] |= view_set_changes[map_section_name] 
##            view_utils.apply_tile_level_changes_to_total_levels(level_changes[map_section_name], self.viewlevelChanges[map_section_name])
##            view_utils.apply_tile_level_changes_to_total_levels(level_changes[map_section_name], self.tilesWithinView[map_section_name])
#        ev = UpdateMap()
#        queue.put(ev)

    def update_known_tiles(self, dict_of_view_changes, update_map = False):
        if dict_of_view_changes:
            newly_known_tiles = {}
            for objectid in dict_of_view_changes:
                object = self.objectIdDict[objectid]
                if object.objtype == 'playerchar':
#                    new_viewed = dict_of_view_changes[objectid][0] | dict_of_view_changes[objectid][1]
                    new_viewed = dict_of_view_changes[objectid][4]
                    map_section_name = object.map_section
                    new_tiles = new_viewed - self.map_data[map_section_name]['known tiles']
                    if new_tiles:
                        if map_section_name not in newly_known_tiles:
                            newly_known_tiles[map_section_name] = new_tiles
                        else:
                            newly_known_tiles[map_section_name] |= new_tiles
                            
                    self.map_data[map_section_name]['known tiles'] |= new_tiles

            if newly_known_tiles:                    
                ev = MakeTilesKnownEvent(newly_known_tiles)
                queue.put(ev)
            
                if update_map:
                    ev = UpdateMap(True)
                    queue.put(ev)
        
        '''
        if viewable_tiles_dict:
            newly_known_tiles = {}
            for objectid in viewable_tiles_dict:
                object_normal_view = viewable_tiles_dict[objectid][0]
                object_dim_view = viewable_tiles_dict[objectid][1]
                object = self.objectIdDict[objectid]
                if object.objtype == 'playerchar':
                    map_section_name = object.map_section
                    new_tiles = object_normal_view - self.map_data[map_section_name]['known tiles']
                    newdim_tiles = object_dim_view - self.map_data[map_section_name]['known tiles']
                    if new_tiles:
                        if map_section_name not in newly_known_tiles:
                            newly_known_tiles[map_section_name] = new_tiles
                        else:
                            newly_known_tiles[map_section_name] |= new_tiles
                    if newdim_tiles:
                        if map_section_name not in newly_known_tiles:
                            newly_known_tiles[map_section_name] = newdim_tiles
                        else:
                            newly_known_tiles[map_section_name] |= newdim_tiles
                            
                    self.map_data[map_section_name]['known tiles'] |= object_normal_view
                    self.map_data[map_section_name]['known tiles'] |= object_dim_view
                    
            ev = MakeTilesKnownEvent(newly_known_tiles)
            queue.put(ev)
            
        if update_map:
            ev = UpdateMap(True)
            queue.put(ev)
        '''
            

    def set_objects_viewable_tiles(self, viewable_tiles_dict, update_map = False):
        if viewable_tiles_dict:
            for objectid in viewable_tiles_dict:
                object_normal_view = viewable_tiles_dict[objectid][0]
                object_dim_view = viewable_tiles_dict[objectid][1]
                object = self.objectIdDict[objectid]
                object.update_viewed_tiles(object_normal_view, object_dim_view)
        if update_map:
            ev = UpdateMap(True)
            queue.put(ev)
            
    def setup_map_data(self):
        for map_section in self.encounter['sections']:
            
            tempdict = {}
            tempdict['monsters'] = set()    # contains monster ids
            if map_section['lighting'] == 'normal':
                tempdict['light'] = {}  # keys are (x,y) tuples, values are light levels
            else:
                tempdict['light'] = 'uniform'
            tempdict['objects'] = set()   # contains object ids
#            tempdict['traps'] = set()       # trap ids
            tempdict['known tiles'] = set()                
            tempdict['fog'] = {}  # for fog, obscuring mist effects, concealment into first, no sight past beyond adjacent tile
                                    # keys are (x,y) tuples, value is a list (will usually just have 1 item) 
                                            # of source dicts (see spells.py), for stuff like fog, etc.                
            tempdict['movement effects'] = {}  # keys are (x,y) tuples, value is a list (will usually just have 1 item) 
                                            # of source dicts (see spells.py), for stuff like grease, etc.                
            tempdict['light effects'] = {}  # keys are (x,y) tuples, value is a list (will usually just have 1 item) 
                                            # of source dicts (see spells.py), for stuff like darkness or light spell, etc.
            tempdict['illusory wall'] = {}  # keys are (x,y) tuples, value is a list (will usually just have 1 item) 
                                            # of source dicts (see spells.py), for spell illusory wall.                
            self.map_data[map_section['name']] = tempdict
            
#            self.viewlevelChanges[map_section['name']] = set()
#            self.tiles_within_party_normal_view[map_section['name']] = set()
#            self.tiles_within_party_dim_view[map_section['name']] = set()

    def distribute_exp_among_party(self, new_exp):
        # done by host
        exp_per_char = new_exp / self.numchars
        exp_dict = {}
        for idx,pcharname in enumerate(self.chars):
            pcharid = self.charnamesid[pcharname]
            exp_dict[pcharid] = exp_per_char
        return exp_dict
    
    def assign_exp_to_party_members(self, exp_dict, reverse = False):
        for pcharid,expval in exp_dict.iteritems():
            pchar = self.objectIdDict[pcharid]
            if not reverse:
                pchar.exp += expval
            else:
                pchar.exp -= expval
        
    def mobj_dies(self, obj):
        # todo - items, treasure, and corpse to ground
        # events of above stuff so view can show them
        return {}
        
    def del_obj(self, obj):
        if obj.objtype == 'monster':
            if obj.id in self.map_data[obj.map_section]['monsters']:
                self.map_data[obj.map_section]['monsters'].discard(obj.id)
        # todo - delete player char
        del self.objectIdDict[obj.id]
        
    def advance_time(self,add_time):
        self.Time += add_time

    def set_time(self,new_time):
        self.Time = new_time
        
    def set_vis(self, dict_of_vis):
        for id,vis in dict_of_vis.iteritems():
            obj = self.objectIdDict[id]
            obj.visible_otherteam_ids = vis[0]
            obj.visible_object_ids = vis[1]
            
    def set_all_subphases(self):
        if turn_mode == 'we_go_they_go':
            for id in self.charnamesid.itervalues():
                obj = self.objectIdDict[id]
                obj.subphase = 10
            for section_name in self.map_section_names:
                for id in self.map_data[section_name]['monsters']:
                    obj = self.objectIdDict[id]
                    obj.subphase = 20

    def processRound(self):
        
        self.saveandload.restoreSave('hostcomplete')
        
        self.mm = self.hostcalcs.ResolveRound()
        
        self.saveandload.restoreSave('player')
        
        ev = HostCalcsDone(self.mm)
        queue.put(ev)

    #----------------------------------------------------------------------
    def Notify(self, event):

#        if isinstance( event, GameStartingEvent ):
#            if self.state == Game.STATE_PREPARING:
#                self.Start()

        if isinstance( event, AllHumanOrdersSubmitted):   # only executed on host
            self.processRound()

       #elif isinstance( event, OrdersDone) and self.numclients == 1:
          #eV = ToggleAllowOrders()    # turn off ability to give orders
          #queue.put(eV)

          #eV = AllHumanOrdersSubmitted()
         #queue.put(eV)

        elif isinstance( event, GameStartedEvent ):
            self.placeUnits()

#        elif isinstance( event, SetTimeEvent ):
#            self.set_time(event.new_time)

        elif isinstance( event, Citycreated):
            self.CreateCity(event.pos, event.cid)

        elif isinstance( event, CitiesAssigned):
            self.assigncities(event.ca)

        elif isinstance( event, Unitcreated):
            self.createUnit(event.type, event.slot, event.pos, event.uid)

        elif isinstance( event, SetEncounterDataEvent):
            self.encounter = event.encounterdata
            
            self.set_map_section_names()
            self.setup_map_data()
            
             
#            self.mapsectionname = self.encounter['possiblestartpos'][0]
#            self.monsters[self.mapsectionname] = []
#            for mon in self.encounter['monstarts']:
#                self.objectIdDict[mon.id] = mon
#                self.monsters[self.mapsectionname].append(mon.id)
#            ec.set_init_char_pos(self.encounter, self)
            client_monster_objects = deepcopy(self.encounter['monstarts'])
            ec.set_monsters(client_monster_objects, self)
            client_objects = deepcopy(self.encounter['obj_locs'])
            ec.set_objects(client_objects, self)
            self.set_all_subphases()
            self.mobile_obj_actions.add_race_effects_all()
            
            self.saveandload.restoreSave('movie')
            self.setup_map_data()
#            ec.set_init_char_pos(self.encounter, self)
            client_monster_objects = deepcopy(self.encounter['monstarts'])
            ec.set_monsters(client_monster_objects, self)
            client_objects = deepcopy(self.encounter['obj_locs'])
            ec.set_objects(client_objects, self)
            self.mobile_obj_actions.add_race_effects_all()
            
            if self.amihost:
                self.saveandload.restoreSave('hostcomplete')
                self.setup_map_data()
#                ec.set_init_char_pos(self.encounter, self)
                ec.set_monsters(self.encounter['monstarts'], self)
                ec.set_objects(self.encounter['obj_locs'], self)
                self.set_all_subphases()
                self.mobile_obj_actions.add_race_effects_all()


#            self.saveandload.restoreSave('player')
#            client_objects = deepcopy(self.encounter['obj_locs'])
#            ec.set_objects(client_objects, self)
#            
#            self.saveandload.restoreSave('movie')
#            client_objects = deepcopy(self.encounter['obj_locs'])
#            ec.set_objects(client_objects, self)
#
#            if self.amihost:
#                self.saveandload.restoreSave('hostcomplete')
#                ec.set_objects(self.encounter['obj_locs'], self)



            self.saveandload.restoreSave('player')
            
            print '************ game, set encounter *********', self.objectIdDict
            
            ec.set_init_char_pos(self.encounter, self)                
#            for idx,pcharname in enumerate(self.chars):
#                pchar = self.objectIdDict[self.charnamesid[pcharname]]
#                pchar.setPosition(self.encounter['charstartlocs'][idx][1])
#                pchar.SetLastOrderedPos(pchar.pos)
#                pchar.set_map_section(self.encounter['charstartlocs'][idx][0])
#                pchar.SetLastOrderedMapSection(pchar.map_section)

            if self.move_mode == 'free':
                ev = EnableDoneButton(False)
                queue.put(ev)

        elif isinstance( event, BuildMapEvent):
            self.map = self.mapmaker.build()
#            self.mapdim = self.map[self.mapsectionname]['dim']

            if self.amihost:
                self.saveandload.restoreSave('hostcomplete')
                map_data_on_lights = view_utils.evaluate_all_light_sources(self)
                self.set_all_lighting(map_data_on_lights)
                dict_of_all_view_info = view_utils.determine_all_view_levels_for_party(self)
                self.set_objects_viewable_tiles(dict_of_all_view_info)
                dict_of_all_monster_view_info = view_utils.determine_all_view_levels_for_monsters(self)
                self.set_objects_viewable_tiles(dict_of_all_monster_view_info)
#                self.update_known_tiles(dict_of_all_view_info)
                dict_of_vis = view_utils.set_all_vis_objects_for_party(self)    # let everything in a viewable tile
                                                                                # be visible at encounter start
                dict_of_mon_vis = view_utils.set_all_vis_objects_for_monsters(self)
                copy_of_map_data_on_lights = deepcopy(map_data_on_lights)
                copy_of_all_view_info = deepcopy(dict_of_all_view_info)
                copy_of_vis = deepcopy(dict_of_vis)
                copy_of_mon_vis = deepcopy(dict_of_mon_vis)
                self.saveandload.restoreSave('player')
                ev = HostSendDataEvent('all_lighting_data', copy_of_map_data_on_lights)
                queue.put(ev)
                ev = HostSendDataEvent('set_all_tiles_within_party_view', copy_of_all_view_info)
                queue.put(ev)
                ev = HostSendDataEvent('set_vis', copy_of_vis)
                queue.put(ev)
                ev = HostSendDataEvent('set_vis', copy_of_mon_vis)
                queue.put(ev)
#                ev = HostSendDataEvent('view_level_changes', copy_of_view_set_changes)
#                queue.put(ev)
            ev = MapBuiltEvent( self.map )
            queue.put(ev)
            
        elif isinstance( event, AssignImportedObjectIdsEvent):
            self.assign_imported_object_ids(event.unified_ids)

        elif isinstance( event, SetAllLightingEvent):
            self.set_all_lighting(event.light_data)
#            ev = MapBuiltEvent( self.map )
#            queue.put(ev)
        elif isinstance( event, SetAllTilesWithinPartyViewEvent):
            view_changes = view_utils.find_dict_of_view_set_changes(event.viewable_tile_sets, self)
            self.set_objects_viewable_tiles(event.viewable_tile_sets)
            self.update_known_tiles(view_changes, True)
            
        elif isinstance( event, SetVisEvent):
            self.set_vis(event.data_dict)
            
        elif isinstance( event, NewItemCreatedEvent ):
            self.objectIdDict[event.item.id] = event.item

#        elif isinstance( event, ChangeViewLevelsEvent):
#            self.change_view_levels(event.view_changes)

       #elif isinstance( event, SetHostAndSlotAndMpdata ):
     #   print 'GAMEGAMENOTIFY', event.mpdata, event.myslot
#         self.amhost = event.amhost
#         self.myslot = event.myslot
#         self.mpdata = event.mpdata

      #elif isinstance( event, Distribute_cnf):
       #   print 'DCNFDCNF'
#           self.cnf = event.cnf

#------------------------------------------------------------------------------
class Player:
    """..."""
    def __init__(self, evManager, nation, playername):
        self.evManager = evManager
        #self.evManager.RegisterListener( self )

        self.nation = nation    # can have more than 1 player controlling a nation (= color)
        self.playername = playername

#------------------------------------------------------------------------------
class Nation:
    """..."""
    def __init__(self, evManager, nation, color, team):
        self.evManager = evManager
        #self.evManager.RegisterListener( self )

        self.nation = nation # can have more than 1 player controlling a nation (= color = nationName)
        self.color = color
        self.team = team

        self.units = []     # contains all individual units
        self.movableObjects = []    # contains objects that can be given move orders
                                    # i.e., doesn't contain units within groups
        #self.ownIdsInViewedOrder = []   # so can keep track of which units are displayed on top
                                        # for things like showing movies, not used?
        self.killedunits = []
        self.movementgroups = []

        self.money = 2000
        
        self.nationorderslist = []
        self.unitorderslist = []

        self.citylist = []
        
        self.premoviesave_units = []
        self.premoviesave_citylist = []
        self.premoviesave_orderslist = []
        self.premoviesave_unitorderslist = []
        self.premoviesave_money = 0
        
        self.postmoviesave_units = []
        self.postmoviesave_citylist = []
        self.postmoviesave_orderslist = []
        self.postmoviesave_unitorderslist = []
        self.postmoviesave_money = 0
        
    def setMgroupOrdersStale(self, game):
        for mgroupid in self.movementgroups:
            mgroup = game.objectIdDict[mgroupid]
            mgroup.ordtimesfresh = False
                


#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
class Mapmaker:
    """..."""
    def __init__(self, evManager, game):
        self.evManager = evManager
        
        self.game = game
        

  #----------------------------------------------------------------------
    def build(self):
        '''
        map
            keys are section names, values are mapsection
            
            mapsection
                keys are: 'dim',       value = tuple of x and y size
                          (x,y),     value = (terrain type, subtype, height) 
                                              todo, expand height into floor_height and ceiling_height
        
        '''
        
        
        allsecdat = self.game.encounter['sections']
        map = {}
        
#        self.sectionnames = []
#        for secdata in allsecdat:
#            self.sectionnames.append(secdata['name'])
            
            
        for secdata in allsecdat:
            map[secdata['name']] = self.buildmapsection(secdata)
            
        return map
        
    def buildmapsection(self, secdata):
        
        msec = {}
        dim = secdata['dim']
        msec['dim'] = dim
        msec['name'] = secdata['name']
        
        btype = secdata['basictype']
        bstype = secdata['basicsubtype']
        bheight = secdata['basicheight']
        for x in range(dim[0]):
            for y in range(dim[1]):
                msec[(x,y)] = (btype, bstype, bheight)
                
        for tersec in secdata['tersecs']:
            ttype = tersec['type']
            tstype = tersec['subtype']
            theight = tersec['height']
            for x in range(tersec['topleft'][0], tersec['bottomright'][0]+1):
                for y in range(tersec['topleft'][1], tersec['bottomright'][1]+1):
                    msec[(x,y)] = (ttype, tstype, theight)
                    
        return msec
        

    def PlaceCity(self):

        # todo: probably need to add increased chance for city loc on coast

        foundgrid = 0
        while not foundgrid:
            #print 'citylocs', self.cityLocsNotUsed
            trialgrid = random.choice(self.cityLocsNotUsed)
            rect = self.citygrids[trialgrid]
            landlocs = []
            for xem in range(rect[0],rect[2]):
                for yem in range(rect[1],rect[3]):
                    if self.elevmap[xem,yem] == 4:  #todo: use lowland_level value here, need to make lowland_level avail
                        landlocs.append((xem,yem))

            #print 'mpc', trialgrid, rect

            self.cityLocsNotUsed.remove(trialgrid)
            if landlocs:
                foundgrid = 1

        emloc = random.choice(landlocs)

        #exactloc = (emloc[0]*8+4, emloc[1]*8+4)
        exactloc = (emloc[0], emloc[1])


        print 'mpc2', emloc, exactloc

        return exactloc

