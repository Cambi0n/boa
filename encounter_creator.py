import os
import yaml
import random
try:
    import cPickle as pickle
except:
    import pickle

from internalconstants import *
from events import *
import monster
import boautils
import object_utils


def MakeLocList(locspec):
    startlocs = []
    for slo in locspec:
        secname = slo[0]
        thisspec = slo[1]
        if thisspec[0] == 'rect':
            thisrect = thisspec[1]
            topleft = thisrect[0]
            bottomright = thisrect[1]
            for x in range(topleft[0], bottomright[0]+1):
                for y in range(topleft[1], bottomright[1]+1):
                    startlocs.append( [secname, (x,y)] )
        else:
            thislist = thisspec[1]
            for xy in thislist:
                startlocs.append( [secname, (xy[0],xy[1])] )
    return startlocs


def AddStuff(game, enc):
    # place chars

    # todo, add monster, traps, other specials
    # todo, make option for random placements
    
    startlocspec = enc['possiblestartpos']
    startlocs = MakeLocList(startlocspec)
    
    charstarts = []
    for np in range(game.numchars):
        st = random.choice(startlocs)
        charstarts.append(st)
        startlocs.remove(st)
        
    enc['charstartlocs'] = charstarts
    
    enc['monstarts'] = []
    if 'monsters' in enc:
        monsterspec = enc['monsters']
        for ms in monsterspec:
            if ms['distribution_type'] == 'placement':
                locspec = ms['startpos']
                locs = MakeLocList(locspec)
                monspecies = ms['species']
#                monsubtype = ms['subtype']
                for i in range(ms['amount']):
                    if locs:
                        thisloc = random.choice(locs)
#                        mon = monster.MonsterClass(montype,monsubtype)
                        mon = monster.MonsterClass(monspecies)
                        mon.setPosition(thisloc[1])
                        mon.SetLastOrderedPos(mon.pos)
                        mon.set_map_section(thisloc[0])
                        mon.SetLastOrderedMapSection(mon.map_section)
                        mon.id = game.giveID()
                        mon.name = game.mobile_obj_actions.find_unique_monster_name(mon, i+1)
                        mon.display_name = mon.name
    #                    game.objectIdDict[mon.id] = mon
                        locs.remove(thisloc)
                        enc['monstarts'].append(mon)
    enc['obj_locs'] = []
    if 'objects' in enc:
        obj_spec = enc['objects']
        for os in obj_spec:
            if os['distribution_type'] == 'placement':
                locspec = os['startpos']
                locs = MakeLocList(locspec)
                oname = os['name']
                for i in range(os['amount']):
                    if locs:
                        thisloc = random.choice(locs)
                        new_item = object_utils.create_new_item(game.master_object_dict[oname],game)
                        new_item.setPosition(thisloc[1])
                        new_item.set_map_section(thisloc[0])
                        locs.remove(thisloc)
                        enc['obj_locs'].append(new_item)
                    
    return enc    

def prepareencs(game):
    
    # the following section would not normally be here
    # either it would just start with loading from disk,
    # or there would be a random generation process
    
    encs = {}
    encs['details'] = []
    encs['desc'] = []
    encs['details'].append('detailed')
    encs['desc'].append('desc')
    encs['details'].append('detailed2')
    encs['desc'].append('desc2')
    
    enc = {}
    enc['desc'] = 'desc'
    level1 = {}
    level1['dim'] = [20,20]
    level1['name'] = 'level1'
    level1['basictype'] = 'floor'
    level1['basicsubtype'] = 'underground1'
    level1['basicheight'] = 0
    level1['lighting'] = 'normal'   # normal means only light near light sources
                                    # other option is 'uniform' for completely lit
                                    # level
    level1['tersecs'] = []
    
    tersec = {}
    tersec['type'] = 'shallow_water'
    tersec['subtype'] = 'shallow1'
    tersec['height'] = 0
    tersec['topleft'] = [9,9]
    tersec['bottomright'] = [11,11]
    level1['tersecs'].append(tersec)
    
    tersec = {}
    tersec['type'] = 'wall'
    tersec['subtype'] = 'granite'
    tersec['height'] = 0
    tersec['topleft'] = [8,16]
    tersec['bottomright'] = [10,16]
    level1['tersecs'].append(tersec)
    
#    tersec = {}
#    tersec['type'] = 'wall'
#    tersec['subtype'] = 'granite'
#    tersec['height'] = 0
#    tersec['topleft'] = [11,17]
#    tersec['bottomright'] = [13,17]
#    level1['tersecs'].append(tersec)
    
    enc['sections'] = [level1]
    enc['possiblestartpos'] = [ ['level1', [ 'rect',[[8,18],[11,19]] ]] ]
#    enc['possiblestartpos'] = [ ['level1', [ 'rect',[[8,18],[8,18]] ]] ]
    
    monster = {}
    monster['distribution_type'] = 'placement'
    monster['type'] = 'orc'
    monster['subtype'] = 'cave'
    monster['amount'] = 1
    monster['startpos'] = [ ['level1', [ 'rect', [[7,5],[12,5]] ]] ]
    
    enc['monsters'] = [monster]
    
    thisfname = 'level2.txt'
    thispath = os.path.join(levelspath, thisfname)
    f = open(thispath, 'w')
    yaml.dump(enc,f) 
    f.close()
    # end of temporary section
    
    
    f = open(thispath, 'r')
    enc2 = yaml.load(f)
    f.close()
    
#    enc2 = AddStuff(game, enc2)
    
    encs['fullencounters'] = []
    encs['fullencounters'].append(enc2)
    encs['fullencounters'].append(enc2)
    
    return encs

def initialize_encounter(game):
    # only host runs this
    game.saveandload.restoreSave('hostcomplete')
#        print 'twnvw', id(self.game.encounters)
    encounter = game.encounters
#        encounter = self.game.saves['hostcomplete'].encounters['fullencounters'][idx]
    game.master_object_dict = build_master_object_dict(game)     # stores data on basic versions
                                                            # of items.
    
    encounter = AddStuff(game, encounter)
    set_init_char_pos(encounter, game)

#    # todo - items won't normally be created this way.  This is a test.
#    # Normally, the player copy of the item object will have been stored in (and loaded from) the character save.
#    # Normally, such items and the their details will have been stored with the character save.
#    # but the actual item object doesn't exist until the host, here, creates it
#    items_to_add = [['backpack','equipped','storage'],['longsword','equipped','mainhand'], ['battleaxe','storage',None], \
#                    ['torch','equipped','offhand'],['holy_symbol_wooden','storage',None]]
#    for pcharname in game.chars:
#        for item in items_to_add:
#            new_item = object_utils.create_new_item(game.master_object_dict[item[0]],game)
#            pickled_item = pickle.dumps(new_item, pickle.HIGHEST_PROTOCOL)
#            ev = HostSendDataEvent('new_item_created', pickled_item)
#            queue.put(ev)
#            profile = game.charsplayer[pcharname]
#            pcharid = game.charnamesid[pcharname]
#            pchar = game.objectIdDict[pcharid]
#            pchar.add_item(new_item,item[1],item[2])
#            item_add_data = [pchar.id, new_item.id, item[1], item[2]]
#            ev = HostSendDataEvent('item_added_to_object', item_add_data)
#            queue.put(ev)
#            if new_item.name == 'torch':
#                new_item.is_showing_light = True
#            
#
#    unified_object_ids = unify_ids_for_imported_objects(game)
#            # unified_object_ids is a dictionary
#            # each key is a tuple of (profile name, character name, old local-to-client-and-char object id)
#            # value is new unified object id
#            
#    game.assign_imported_object_ids(unified_object_ids)
#
#    print 'encounter creator, init encounter1', game.objectIdDict
#    # todo - items won't normally be created this way.  This is a test
#    items_to_add = [['backpack','equipped','storage'],['longsword','equipped','mainhand'], ['battleaxe','storage',None], \
#                    ['torch','equipped','offhand'],['holy_symbol_wooden','storage',None]]
#    for pcharname in game.chars:
#        for item in items_to_add:
#            new_item = object_utils.create_new_item(game.master_object_dict[item[0]],game)
#            game.objectIdDict[new_item.id] = new_item
#            pickled_item = pickle.dumps(new_item, pickle.HIGHEST_PROTOCOL)
#            ev = HostSendDataEvent('new_item_created', pickled_item)
#            queue.put(ev)
#            profile = game.charsplayer[pcharname]
#            pcharid = game.charnamesid[pcharname]
#            pchar = game.objectIdDict[pcharid]
#            pchar.add_item(new_item,item[1],item[2])
##            ev = AddItemToGameObjectEvent(pchar, new_item, item[1], item[2])
##            queue.put(ev)
#            item_add_data = [pchar.id, new_item.id, item[1], item[2]]
#            ev = HostSendDataEvent('item_added_to_object', item_add_data)
#            queue.put(ev)
#            if new_item.name == 'torch':
#                new_item.is_showing_light = True
#        
#    print 'encounter creator, init encounter2', game.objectIdDict
#    
#    # create new item
#    # send new_item_created from host to clients
#    # put new item somewhere
#    # send place_item from host to clients
    
#    set_monsters(encounter['monstarts'], game)
    
    # check and set lighting levels here and add to encounter dictionary
    
#        for idx2,pcharname in enumerate(self.game.chars):
#            pcharid = self.game.charnamesid[pcharname]
#            pchar = self.game.objectIdDict[pcharid]
#            pchar.setPostion( encounter['charstartlocs'][idx2][1] )
#            pchar.SetLastOrderedPos(pchar.pos)
#            pchar.set_map_section(encounter['charstartlocs'][idx2][0])
#            pchar.SetLastOrderedMapSection(pchar.map_section)
    
#        for idx2,pcharname in enumerate(self.game.saves['hostcomplete'].chars):
#            pcharid = self.game.saves['hostcomplete'].charnamesid[pcharname]
#            pchar = self.game.saves['hostcomplete'].objectIdDict[pcharid]
#            pchar.pos = encounter['charstartlocs'][idx2]
#            pchar.lastOrderedPos = pchar.pos

    game.saveandload.restoreSave('player')
    
#    return encounter, unified_object_ids
    return encounter
    

def set_init_char_pos(encounter, game):
    for idx,pcharname in enumerate(game.chars):
        pcharid = game.charnamesid[pcharname]
        pchar = game.objectIdDict[pcharid]
        pchar.setPosition( encounter['charstartlocs'][idx][1] )
        pchar.SetLastOrderedPos(pchar.pos)
        pchar.set_map_section( encounter['charstartlocs'][idx][0] )
        pchar.SetLastOrderedMapSection(pchar.map_section)
        itemslist = pchar.list_items(listall = True)
        for item in itemslist:
            item.setPosition(pchar.pos)  
        
    
def set_monsters(monlist, game):
    for mon in monlist:
        game.objectIdDict[mon.id] = mon
        game.map_data[mon.map_section]['monsters'].add(mon.id)
       
def set_objects(objlist, game):
    for obj in objlist:
        game.objectIdDict[obj.id] = obj
        print '************* ec, set obj **********', obj, obj.name, obj.pos, game.objectIdDict, game
        game.map_data[obj.map_section]['objects'].add(obj.id)
       
def unify_ids_for_imported_objects(game):
    # only host runs this
    
    unified_ids = {}
    for pcharname in game.chars:
        profile = game.charsplayer[pcharname]
        pcharid = game.charnamesid[pcharname]
        pchar = game.objectIdDict[pcharid]
        itemslist = pchar.list_items(listall = True)
        for item in itemslist:
            old_id = item.id
            new_id = game.giveID()
            if (profile,pcharname,old_id) in unified_ids:
                print 'duplicate old ids for character ', profile, pcharname, item.name
                print 'switching to item id, name, type, and weight'
                unified_ids[(profile,pcharname,old_id,item.name,item.type,item.weight)] = new_id
            else:
                unified_ids[(profile,pcharname,old_id)] = new_id
            item.assign_id(new_id)
            game.objectIdDict[new_id] = item
    return unified_ids

def build_master_object_dict(game):
    obj_dict = {}

    dirs_under_path = boautils.listDirectories(defaultgamepath)
    if 'objects' in dirs_under_path:
        obj_dir = os.path.join(defaultgamepath,'objects')
        obj_files = boautils.listFiles(obj_dir)
        
    for obj_file in obj_files:
        this_file_with_path = os.path.join(obj_dir,obj_file)
        f = open(this_file_with_path, 'r')
        obj_list = yaml.safe_load(f)
        f.close()
        
        for obj in obj_list:    # obj is a dict of a single object
            obj_dict[obj['name']] = obj
    

    enc_path = game.town.enc_path
    dirs_under_enc_path = boautils.listDirectories(enc_path)
    
    if 'objects' in dirs_under_enc_path:
        obj_dir = os.path.join(enc_path,'objects')
        obj_files = boautils.listFiles(obj_dir)
        
    for obj_file in obj_files:
        this_file_with_path = os.path.join(obj_dir,obj_file)
        f = open(this_file_with_path, 'r')
        obj_list = yaml.safe_load(f)
        f.close()
        
        for obj in obj_list:    # obj is a dict of a single object
            obj_dict[obj['name']] = obj     # overwrite as needed
        
    return obj_dict
    