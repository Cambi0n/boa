'''
Created on Jul 3, 2010

@author: bdf
'''
import Queue
#import copy as cpy
from copy import deepcopy
try:
    import cPickle as pickle
except:
    import pickle

from events import *
from evmanager import *
from userconstants import *
import view_utils
import inventory_popup
#import info_dialog_utils
#from units import Unit
#from gamefunctions import adjustViewLevels

class ClientRoundResults:
    def __init__(self,game,evManager, view):
        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )
        
        self.game = game
        self.view = view
        
#        self.free_move_results_blocked = False
        self.free_move_results = []
        
        self.unitsToDelete = []
        
    def executeHostEvents(self,natorders):
        for nato in natorders:
            if nato[0] == 'unit id assigned':
                unit = self.game.tempIdDict[nato[1]]
                unit.id = nato[2]
                del self.game.tempIdDict[nato[1]]
                self.game.objectIdDict[unit.id] = unit
#                print 'in client results', unit.id
        
    def setGameToPulse(self, setpulsenum, currentpulse, effectslist, doEndOfPulseCleanup):
#        print 'clientturnresults', setpulsenum, currentpulse
        if setpulsenum > self.game.tot_num_pulses:
            setpulsenum = int(self.game.tot_num_pulses)
        elif setpulsenum < 0:
            setpulsenum = 0
        if setpulsenum > currentpulse:
            movedir = 1
        else:  
            movedir = -1
        if setpulsenum == currentpulse:
            return
        
#        print 'setgametopulse', setpulsenum,currentpulse
            
#        for np in range(int(numpulses)):
#            self.visevents.append([])
            
        
        for pulsenum in range(currentpulse,setpulsenum,movedir):
            self.visevents.append([])
            if movedir == 1:
                ordlist = effectslist[pulsenum]
            else:
                ordlist = effectslist[pulsenum-1]
            numorders_thispulse = len(ordlist)
            if movedir == 1:
                ordnumlist = range(numorders_thispulse)
            else:
                ordnumlist = range(numorders_thispulse-1,-1,-1)
            for ordnum in ordnumlist:
                thisorder = ordlist[ordnum]
                uid = thisorder[0]
                ordtype = thisorder[1]
    
                if ordtype == 'move':
                    unit = self.game.objectIdDict[uid]
#                    print 'in clientturnresults, move', pulsenum, unit.objtype, unit.pos, thisorder, unit.orders 
                    print 'in clientroundresults, move', pulsenum, unit.objtype, unit.pos, thisorder, unit, unit.id 
#                    if unit.nation == self.game.mynation:
#                        if unit.orders[0][0] != 'pursue target':
#                            unit.orders[0][1].pop(0)
#                        else:
#                            unit.lastOrderedPos = thisorder[2]
                    if unit.objtype == 'movementgroup':
                        for membid in unit.members:
                            memb = self.game.objectIdDict[membid]
                            print 'in clientroundresults, move2', memb.orders
                            orddat = [membid,'move',thisorder[2],memb.pos]
                            self.visevents[pulsenum].append(orddat)
                    else:
                        orddat = [uid,'move',thisorder[2],unit.pos]
                        self.visevents[pulsenum].append(orddat)
                    unit.setPosition(thisorder[2])
                    unit.popPath(self.game)
                    if not unit.orders and self.game.move_mode == 'free' and unit.before_order_decisions:
                        self.handle_before_order_decisions(unit)
                        
                    
                elif ordtype == 'set lop':
                    unit = self.game.objectIdDict[uid]
                    orddat = [uid,'set lop',thisorder[2],unit.pos]
                    self.visevents[pulsenum].append(orddat)
                    unit.SetLastOrderedPos(thisorder[2])
                        
                elif ordtype == 'pop0':
#                    print 'in clientturnresults, pop0', pulsenum, unit.objtype, unit.pos, thisorder, unit.orders
#                    print 'in clientroundresults, pop0', pulsenum, unit.objtype, unit.pos, thisorder
                    unit = self.game.objectIdDict[uid]
                    unit.pop_order(0)
                    orddat = [uid,'pop0',thisorder[2]]
                    self.visevents[pulsenum].append(orddat)
                    if not unit.orders and self.game.move_mode == 'free' and unit.before_order_decisions:
                        self.handle_before_order_decisions(unit)
                    
                elif ordtype == 'light_changes':
                    light_level_changes = thisorder[2]
                    map_section_name = thisorder[3]
                    view_utils.apply_tile_level_changes_to_total_levels(light_level_changes, self.game.map_data[map_section_name]['light'])
                    orddat = ['game', 've_light_changes', light_level_changes, map_section_name]
                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'new_viewed_tiles':
                    dict_of_view_info = thisorder[2]
                    dict_of_view_changes = view_utils.find_dict_of_view_set_changes(dict_of_view_info, self.game)
                    self.game.set_objects_viewable_tiles(dict_of_view_info)
                    self.game.update_known_tiles(dict_of_view_changes)
                    orddat = ['game', 've_new_viewed_tiles', dict_of_view_info, dict_of_view_changes]
                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'mover_vis_changes':
                    mover_vis_changes = thisorder[2]
                    unit = self.game.objectIdDict[uid]
                    unit.apply_vis_changes(**mover_vis_changes)
                    orddat = [uid, 've_mover_vis_changes', mover_vis_changes]
                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'others_vis_changes_of_mobj':
                    nonmover_vis_changes = thisorder[2]
                    view_utils.apply_others_vis_changes_of_mobj_id(uid, nonmover_vis_changes, self.game)
                    orddat = [uid, 've_others_vis_changes_of_mobj', nonmover_vis_changes]
                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'others_vis_changes_of_nonmobj':
                    vis_changes = thisorder[2]
                    view_utils.apply_others_vis_changes_of_nonmobj_id(uid, vis_changes, self.game)
                    orddat = [uid, 've_others_vis_changes_of_nonmobj', vis_changes]
                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'missed attack on enemy':
                    tohit_roll = thisorder[3]
                    print 'ctr, missed', tohit_roll
                
                elif ordtype == 'enemy missed attack':
                    pass
                
                elif ordtype == 'damage dealt':
                    details = thisorder[2]
                    enemyid = details['enemy_id']
                    dam_tot_list = details['damage_total']
                    dam_tot = 0
                    for dam in dam_tot_list:
                        dam_tot += dam
                    enemy_obj = self.game.objectIdDict[enemyid]
                    enemy_obj.change_damage(dam_tot)
                    orddat = [uid, 've damage dealt', details]
                    self.visevents[pulsenum].append(orddat)
                    tohit = details['tohit_roll']
                    print 'ctr, damage dealt', tohit, dam_tot
                
                elif ordtype == 'received damage':
                    pass
                
                elif ordtype == 'assign exp':
                    exp_dict = thisorder[2]
                    self.game.assign_exp_to_party_members(exp_dict)
                    orddat = [uid, 've assign exp', exp_dict]
                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'lose vis of id':
                    lostid = thisorder[2]
                    ids_that_see = thisorder[3]
                    print 'clientroundresults, lose vis of id', lostid, ids_that_see
                    view_utils.remove_id_from_other_vis_lists(lostid, ids_that_see, self.game)
                    orddat = ['game', 've lose vis of id', lostid, ids_that_see]
                    self.visevents[pulsenum].append(orddat)
                
                elif ordtype == 'dead':
                    dead_obj = self.game.objectIdDict[uid]
                    self.game.del_obj(dead_obj)
                    orddat = [uid, 've dead', thisorder[2]]
                    self.visevents[pulsenum].append(orddat)

                elif ordtype == 'update actions used':
                    char = self.game.objectIdDict[uid]
                    change = thisorder[2]
                    char.update_actions_used(change)

                elif ordtype == 'time passed':
                    self.game.advance_time(thisorder[2])
#                    self.game.Time += thisorder[2]

                elif ordtype == 'set time':
                    self.game.set_time(thisorder[2])
                        
                elif ordtype == 'change to phased mode':
                    self.game.move_mode = 'phased'
                    ev = EnableDoneButton(True)
                    queue.put(ev)
                    ev = HideModalWindowEvent()
                    queue.put(ev)
                    ev = HideModalWindowEvent()     # in case both primary and secondary modal windows are up
                    queue.put(ev)
                    ev = HideModalWindowEvent()     # todo - need to create function to hide all modal windows
                                                    # since number isn't limited any more.
                    queue.put(ev)
                    idlist = self.game.charnamesid.values()
                    for id in idlist:
                        playerchar = self.game.objectIdDict[id]
                        playerchar.SetLastOrderedPos(playerchar.pos, self.game)
                    
                elif ordtype == 'add effect':
                    num_entries = len(thisorder)
                    details = thisorder[2]
                    if num_entries >= 4:
                        effect_func_str_dict = thisorder[3]
                    else:
                        effect_func_str_dict = {}
                    if num_entries >= 5:
                        dispells = thisorder[4]
                    else:
                        dispells = []
                    target = self.game.objectIdDict[uid]
                    target.add_temporary_effect(details, self.game, effect_func_str_dict, dispells)
                    orddat = [uid, 've add effect', thisorder[2:]]
                    self.visevents[pulsenum].append(orddat)
                    
#                elif ordtype == 'add bonus':
#                    details = thisorder[2]
#                    target = self.game.objectIdDict[uid]
#                    target.add_bonus(details)
#                    orddat = [uid, 've add bonus', details]
#                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'effect_expiring':
                    details = thisorder[2]
                    target = self.game.objectIdDict[uid]
                    target.remove_temporary_effect(details)
                    orddat = [uid, 've remove effect', details]
                    self.visevents[pulsenum].append(orddat)

                elif ordtype == 'create new item':
                    pickled_item = thisorder[2]
                    new_item = pickle.loads(pickled_item)
                    self.game.objectIdDict[new_item.id] = new_item
                    
                    orddat = ['game', 've create new item', pickled_item]
                    self.visevents[pulsenum].append(orddat)

                elif ordtype == 'add item to object':
                    item_id = thisorder[2]
                    loc = thisorder[3]
                    slot = thisorder[4]
                    obj = self.game.objectIdDict[uid]
                    item = self.game.objectIdDict[item_id]
                    obj.add_item(item, loc, slot)
                    orddat = [uid, 've add item to object', thisorder[2:]]
                    self.visevents[pulsenum].append(orddat)

                elif ordtype == 'remove item from object':
                    item_id = thisorder[2]
                    obj = self.game.objectIdDict[uid]
                    item = self.game.objectIdDict[item_id]
                    obj.remove_item_no_loc(item)
                    orddat = [uid, 've remove item from object', thisorder[2]]
                    self.visevents[pulsenum].append(orddat)

                elif ordtype == 'delete object from id':
                    item_id = thisorder[2]
                    del self.game.objectIdDict[item_id]
                    orddat = ['game', 've delete object from id', thisorder[2]]
                    self.visevents[pulsenum].append(orddat)

                elif ordtype == 'set new orders':
                    new_orders = thisorder[2]
                    mobj = self.game.objectIdDict[uid]
                    old_orders = deepcopy(mobj.orders) 
                    mobj.set_new_orders(new_orders, self.game)
                    orddat = [uid, 've set new orders', deepcopy(new_orders), old_orders]
                    self.visevents[pulsenum].append(orddat)

                elif ordtype == 'append new order':
                    new_orders = thisorder[2]
                    mobj = self.game.objectIdDict[uid]
                    mobj.orders.append(new_orders)
                    orddat = [uid, 've append new order', deepcopy(new_orders)]
                    self.visevents[pulsenum].append(orddat)

                elif ordtype == 'drop item':
                    mobj = self.game.objectIdDict[uid]
                    item = self.game.objectIdDict[thisorder[2]]
                    print '$$$$$$$$$$$$$$$$ dropping item on client $$$$$$$$$$$$$$$$$$$$'
                    mobj.drop_item(item, self.game)
                    if self.game.move_mode == 'free':
                        if self.view.pguctrl.modal_window_instances != []:
                            if isinstance(self.view.pguctrl.modal_window_instances[-1], inventory_popup.InventoryScreenWrapper):
                                self.view.pguctrl.hide_modal_window()
                                self.view.uv.right_click_menu_class.show_inventory_screen()

                    orddat = [uid, 've drop item', item.id]
                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'pickup item':
                    mobj = self.game.objectIdDict[uid]
                    item = self.game.objectIdDict[thisorder[2]]
                    mobj.pickup_item(item, self.game)
#                    if self.game.move_mode == 'free':
#                        if isinstance(self.view.pguctrl.modal_window_instance, inventory_popup.InventoryScreenWrapper):
#                            self.view.pguctrl.hide_modal_window()
#                            self.view.uv.right_click_menu_class.show_inventory_screen()

                    orddat = [uid, 've pickup item', item.id]
                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'forced drop item':
                    mobj = self.game.objectIdDict[uid]
                    item = self.game.objectIdDict[thisorder[2]]
                    mobj.drop_item(item, self.game)

                    orddat = [uid, 've forced drop item', item.id]
                    self.visevents[pulsenum].append(orddat)
                    
                elif ordtype == 'show message':
                    if self.game.move_mode == 'free':
                        if uid == 'game' or uid in self.game.charnamesid.itervalues():
                            self.view.show_timed_msg(thisorder[2], True)
#                            self.view.add_client_msg(surf)
                    else:
                        orddat = [uid, 've show message', thisorder[2]]
                        self.visevents[pulsenum].append(orddat)
                        
                    
                elif ordtype == 'client call func':
                    other_data = thisorder[2]
                    source = other_data[0]
                    func_str = other_data[1] 
                    if len(other_data) >= 3:
                        extra = other_data[2]
                    else:
                        extra = None
                    self.call_client_func(source, func_str, extra)
                    
#                elif ordtype == 'client call func blocking':
#                    self.free_move_results_blocked = True
#                    other_data = thisorder[2]
#                    source = other_data[0]
#                    func_str = other_data[1] 
#                    if len(other_data) >= 3:
#                        extra = other_data[2]
#                    else:
#                        extra = None
#                    self.call_client_func(source, func_str, extra)
                    
                elif ordtype == 'call function before orders':
                    mobj = self.game.objectIdDict[uid]
                    mobj.add_before_order_decision(thisorder[2])
                    if not mobj.orders and self.game.move_mode == 'free' and mobj.before_order_decisions:
                        self.handle_before_order_decisions(mobj)
                            
                elif ordtype == 'add spell concentration data':
                    mobj = self.game.objectIdDict[uid]
                    mobj.add_spell_concentration_data(thisorder[2])
                    
                # todo - fully implement next 6 items
                elif ordtype == 'attempted saving throw':
                    save_details = thisorder[2]
                    
                elif ordtype == 'forced enemy saving throw':
                    save_details = thisorder[2]
                    
                elif ordtype == 'attempted spell resistance':
                    sr_details = thisorder[2]

                elif ordtype == 'forced enemy spell resistance check':
                    sr_details = thisorder[2]
                            
                elif ordtype == 'did perception check':
                    perception_details = thisorder[2]
                    stealth_details = thisorder[3]
                            
                elif ordtype == 'did stealth check to oppose perception':
                    stealth_details = thisorder[2]
                            
    def call_client_func(self, source, func_str, extra):
        this_class = None
        if 'spell_name' in source:
            this_class = self.game.complete_dict_of_spells[source['spell_name']]
        elif 'condition_name' in source:
            this_class = self.game.dict_of_conditions[source['condition_name']]
        elif 'race_name' in source:
            this_class = self.game.dict_of_races[source['race_name']]
            
        if this_class:
            func = getattr(this_class, func_str)
            if hasattr(func, '__call__'):
                func(source,extra)

    def handle_before_order_decisions(self, obj):
        for dec in obj.before_order_decisions:
            source = dec[0]
            func_str = dec[1] 
            if len(dec) >= 3:
                extra = dec[2]
            else:
                extra = []
            extra.append(self.game)
            print '###############  client roundresults, hand before turnB ############', extra
            self.call_client_func(source, func_str, extra)
        obj.before_order_decisions = []
        print '############## client roundresults, hand before turn ############'
#        ev = SpriteSelectedEvent(sprite, True)
#        queue.put(ev)
        
                        
    def endOfPulseCleanup(self):
        
        for u in self.unitsToDelete:
            self.game.unitActions.deleteUnit(u)
            
        self.unitsToDelete = []

    def betweenRoundCleanup(self, Nation):
        Nation.setMgroupOrdersStale(self.game)
        
    def all_chars_refresh_at_round_start(self):
        for charname in self.game.playerschars[self.game.myprofname]:
            charid = self.game.charnamesid[charname]
            char = self.game.objectIdDict[charid]
            char.refresh_at_round_start(self.game)
        ev = ClearSelectionEvent()
        queue.put(ev)        

    def Notify(self, event):

        if isinstance( event, SetTimeEvent ):
            self.game.set_time(event.new_time)
            
        elif isinstance(event, RoundResolved):
            print 'ctr1000'
#            eV = ClearSelectionEvent(False)
#            queue.put(eV)
            
            self.visevents = []
            self.setGameToPulse(int(self.game.tot_num_pulses), 0, event.mm, False)
            
            self.all_chars_refresh_at_round_start()
            
#            self.betweenRoundCleanup(Nation)

            self.game.saveandload.restoreSave('movie')
            eV = ShowMovie(self.visevents )
            queue.put(eV)
            
            self.game.advance_time(seconds_per_round*1000)
#            self.game.Time += seconds_per_round
            
        elif isinstance( event, FreeMoveResultsEvent ):
            
            self.visevents = []
            new_ord_list = event.orddat
            self.free_move_results.extend(new_ord_list)
            
            idxs_to_remove = []
            for idx,ord in enumerate(self.free_move_results):
                temp_orddat = []
                temp_orddat.append([ord])
                self.setGameToPulse(1, 0, temp_orddat, False)
                idxs_to_remove.append(idx)
            for idx in reversed(idxs_to_remove):
                self.free_move_results.pop(idx)
                
            self.view.uv.refreshAllVisSprites()

#            idxs_to_remove = []
#            for idx,ord in enumerate(self.free_move_results):
#                if not self.free_move_results_blocked:
#                    temp_orddat = []
#                    temp_orddat.append([ord])
#                    self.setGameToPulse(1, 0, temp_orddat, False)
#                    idxs_to_remove.append(idx)
#                else:
#                    break
#            for idx in reversed(idxs_to_remove):
#                self.free_move_results.pop(idx)
#                
#            if not self.free_move_results_blocked:
#                self.view.uv.refreshAllVisSprites()
            
#        elif isinstance( event, UnblockFreeMoveResultsOnClientEvent ):
#            self.free_move_results_blocked = False                
                
                
                
#            temp_orddat.append(event.orddat)
#            print '########## ctr, free move event ##############', event.orddat
#            self.setGameToPulse(1, 0, temp_orddat, False)
#            if not (len(event.orddat) == 1 and event.orddat[0][1] == 'set time'):
#                self.view.uv.refreshAllVisSprites()
#            eV = RefreshAllSpritesEvent()
#            queue.put(eV)
            

        
        