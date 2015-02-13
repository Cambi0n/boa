
from math import *
import random

#import operator
from operator import itemgetter

import game as gamec
#from game import *
from gamefunctions import *
from userconstants import *
from copy import deepcopy
import view_utils
from internalconstants import *



# todo: will need to flag units that are destroyed in combat this round
# then truly delete them the following round

class HostGameCalcs:
    def __init__(self, game):
        self.game = game
        self.time_per_pulse = int(round(seconds_per_round * 1000. / num_pulses_per_unit))

    def ResolveRound(self):

        del hctp_orddat[:]    #
        global np
        np = 0 
#        self.dcs = []   # detections, combat losses, supply changes
        
        self.prepareEmptyOutgoingOrderList()    # creates hctp_orddat structure

        self.pseudo_game_time = self.game.Time
        end_of_round_time = self.game.Time + (seconds_per_round * 1000)

        effects_timed_event_list.sort(key=itemgetter(0,1))
        timed_events_occurring = find_timed_events_occurring(effects_timed_event_list, end_of_round_time, 9)
        handle_game_timed_events(timed_events_occurring, self.game)

        for prof in self.game.players:
            for charname in self.game.playerschars[prof]:
                charid = self.game.charnamesid[charname]
                char = self.game.objectIdDict[charid]
                char.orders_summary = summarize_orders(charid, self.game)
                evaluate_next_order(char, self.game)
                for omo in char.other_movable_objects:
                    evaluate_next_order(omo, self.game)
        for i in range(int(num_pulses_per_unit)):
            np = i
            self.pseudo_game_time += self.time_per_pulse
            orders_timed_event_list.sort(key=itemgetter(0,1))
            print 'hgc', np
            timed_events_occurring = find_timed_events_occurring(orders_timed_event_list, self.pseudo_game_time,10)
            handle_game_timed_events(timed_events_occurring, self.game)

        effects_timed_event_list.sort(key=itemgetter(0,1))
        timed_events_occurring = find_timed_events_occurring(effects_timed_event_list, end_of_round_time, 11)
        handle_game_timed_events(timed_events_occurring, self.game)

        effects_timed_event_list.sort(key=itemgetter(0,1))
        timed_events_occurring = find_timed_events_occurring(effects_timed_event_list, end_of_round_time, 19)
        handle_game_timed_events(timed_events_occurring, self.game)

        idlist = []
        for section_name in self.game.map_section_names:
            idlist.extend(self.game.map_data[section_name]['monsters'])
        for mid in idlist:
            obj = self.game.objectIdDict[mid]
            self.reset_obj(obj)

        np = int(num_pulses_per_unit)
        self.game.ai.order_all_moves()
        self.pseudo_game_time = self.game.Time
        for section_name in self.game.map_section_names:
            for monid in self.game.map_data[section_name]['monsters']:
                mon = self.game.objectIdDict[monid]
                mon.orders_summary = summarize_orders(monid, self.game)
                evaluate_next_order(mon, self.game)
        for i in range(int(num_pulses_per_unit), int(self.game.tot_num_pulses)):
            np = i
            self.pseudo_game_time += self.time_per_pulse
            orders_timed_event_list.sort(key=itemgetter(0,1))
            print 'hgc', np
            timed_events_occurring = find_timed_events_occurring(orders_timed_event_list, self.pseudo_game_time,20)
            handle_game_timed_events(timed_events_occurring, self.game)
            
        effects_timed_event_list.sort(key=itemgetter(0,1))
        timed_events_occurring = find_timed_events_occurring(effects_timed_event_list, end_of_round_time, 21)
        handle_game_timed_events(timed_events_occurring, self.game)

        self.game.Time += (seconds_per_round * 1000)      

#        effects_timed_event_list.sort(key=itemgetter(0,1))
#        timed_events_occurring = find_timed_events_occurring(effects_timed_event_list, self.game.Time,0)
#        handle_game_timed_events(timed_events_occurring, hctp_orddat[self.np], self.game)
       
        other_timed_event_list.sort(key=itemgetter(0,1))
        timed_events_occurring = find_timed_events_occurring(other_timed_event_list, self.game.Time,0)
        handle_game_timed_events(timed_events_occurring, self.game)

        self.end_of_round_reset()   # need to do this before orders are chosen, so do it at end of round for chars  

        return hctp_orddat

    def end_of_round_reset(self):
        # todo - monsters need to refresh also
#        np = int(self.game.tot_num_pulses)-1

#        idlist = []
#        for section_name in self.game.map_section_names:
#            idlist.extend(self.game.map_data[section_name]['monsters'])
#        idlist.extend(self.game.charnamesid.itervalues())
        for id in self.game.charnamesid.itervalues():
            obj = self.game.objectIdDict[id]
            self.reset_obj(obj)
                    

    def reset_obj(self,obj):
        obj.update_actions_used('clear all')
        orddat = [obj.id, 'update actions used', 'clear all']
        hctp_orddat[np].append(orddat)
        if obj.is_fleeing(self.game):
            flee_entry = obj.find_flee_effect_entry()
            if flee_entry:
                source = flee_entry[0][2]
                if 'obj_id' in source:
                    target_id = source['obj_id']
                    target = self.game.objectIdDict[target_id]
                    movement_points = obj.find_movespeed()*2
                    path = find_flee_path(obj,target,movement_points,self.game)
                    new_ords = ['move', path]
                    obj.set_new_orders([new_ords], self.game)
                    ord = [obj.id, 'set new orders', deepcopy([new_ords])]
                    hctp_orddat[np].append(ord)
        obj.stealth_already_checked = False
                
        
#        for prof in self.game.players:
#            for charname in self.game.playerschars[prof]:
#                charid = self.game.charnamesid[charname]
#                char = self.game.objectIdDict[charid]
#                char.update_actions_used('clear all')
#                orddat = [charid, 'update actions used', 'clear all']
#                hctp_orddat[np].append(orddat)

    def prepareEmptyOutgoingOrderList(self):
#        for prof in self.game.players:
#            hctp_orddat[prof] = []
        for i in range(int(self.game.tot_num_pulses)):
            hctp_orddat.append([])
        
#    def one_pulse_for_one_mobj(self, mo):
#        new_mobjs = []
#        remove_mobjs = []
#        while self.modict[mo.id] == self.np:
#            ord = mo.orders[0]
#            if ord[0] == 'move': 
#                self.move_square(mo)
#            elif ord[0] == 'standard_attack':
#                print 'hgc, opfom, standard attack', ord
#                self.do_standard_attack(mo, ord[1], ord[2], ord[3])
#            elif ord[0] == 'cast_spell':
#                cast_spell(mo, ord[1], ord[2], self.game, hctp_orddat[self.np])
#                
#            self.modict[mo.id] = find_pulse_for_next_action(self.game,mo.id,self.np)            
#                
#        return new_mobjs, remove_mobjs
#            
#    def move_square(self, mo):
#        path = mo.orders[0][1]
#        nextsq = path[0]
#        oldpos = mo.pos
#        mo.setPosition(nextsq)
#        mo.popPath(self.game)
#        orddat = [mo.id, 'move', mo.pos, oldpos]
#        hctp_orddat[self.np].append(orddat)
#        vis_and_light_changes_from_move(mo, self.game, hctp_orddat[self.np], oldpos)


def do_standard_attack(mo, enemy_id, source, game, event_time, ddl = None):
    # source is a string which specifies where the attack is coming from
    # such as mainhand, bothhands, claw, bite, spit, etc.
    # ddl stands for damage_details_list.  for regular attacks, this will be calculated
    # in calc_damage_dice.  For spell based attackes, this will be provided by spell effect.
    orddat = hctp_orddat[np]
    enemy_obj = game.objectIdDict[enemy_id]
    base_attack_bonuses = mo.find_base_attack_bonuses(enemy_obj)
    if source['attack_type'] == 'melee':
        execute_melee_attack(mo, enemy_obj, base_attack_bonuses[0], source, game)
    elif source['attack_type'] == 'ranged':
        execute_ranged_attack(mo, enemy_obj, base_attack_bonuses[0], source, game)
    elif source['attack_type'] == 'melee touch':
        execute_melee_touch_attack(mo, enemy_obj, base_attack_bonuses[0], source, game, ddl)
    orddat.append([mo.id, 'pop0', mo.orders[0]])
    mo.pop_order(0)
    evaluate_next_order(mo, game, event_time)
    
def do_drop_item(mo, item, game, event_time):
    orddat = hctp_orddat[np]
    print '*********** droping item on host ***************'
    mo.drop_item(item,game)
    vis_changes = find_others_vis_changes_of_this_nonmobj_id(item.id, game)
    view_utils.apply_others_vis_changes_of_nonmobj_id(item.id, vis_changes, game)
    if vis_changes[0] or vis_changes[1]:
        orddat.append([item.id, 'others_vis_changes_of_nonmobj', vis_changes])
    
#    view_utils.check_for_and_apply_vis_changes_of_nonmoving_object(item,game)     
    orddat.append([mo.id, 'pop0', mo.orders[0]])
    mo.pop_order(0)
    evaluate_next_order(mo, game, event_time)
    
def do_pickup_item(mo, item, game, event_time):
    orddat = hctp_orddat[np]
    mo.pickup_item(item,game)
    vis_changes = find_others_vis_changes_of_this_nonmobj_id(item.id, game, remove_vis = True)
    view_utils.apply_others_vis_changes_of_nonmobj_id(item.id, vis_changes, game)
    if vis_changes[0] or vis_changes[1]:
        orddat.append([item.id, 'others_vis_changes_of_nonmobj', vis_changes])
    
#    view_utils.check_for_and_apply_vis_changes_of_nonmoving_object(item,game)     
    orddat.append([mo.id, 'pop0', mo.orders[0]])
    mo.pop_order(0)
    evaluate_next_order(mo, game, event_time)
    
def forced_drop_item(mo, item, game, event_time):
    # dropping an item, but no order in mo.orders
    # typically forced by something else
    mo.drop_item(item,game)

def execute_melee_attack(mo, enemy_obj, attack_bonus, source, game):
    tohit_bonus = mo.calc_melee_tohit_bonus(enemy_obj, game, source) + attack_bonus
    miss_chance = enemy_obj.calc_miss_chance(game,source)
    armor_class = enemy_obj.calc_armor_class(mo, game, source)
    damage_details_list = calc_damage_dice(mo, enemy_obj, source, game)
    execute_attack(mo, enemy_obj, tohit_bonus, miss_chance, damage_details_list, armor_class, game, source)

def execute_ranged_attack(self, mo, enemy_obj, attack_bonus, source, game):
    pass

def execute_melee_touch_attack(mo, enemy_obj, attack_bonus, source, game, ddl):
    tohit_bonus = mo.calc_melee_tohit_bonus(enemy_obj, game, source) + attack_bonus
    miss_chance = enemy_obj.calc_miss_chance(mo,game,source)
    armor_class = enemy_obj.calc_armor_class(mo, game, source)
#    damage_details_list = calc_damage_dice(mo, enemy_obj, source, game)
    execute_attack(mo, enemy_obj, tohit_bonus, miss_chance, ddl, armor_class, game, source)
    
def vis_and_light_changes_from_move(obj, game, oldpos, stealth_move = False):
    orddat = hctp_orddat[np]
    light_level_changes, dict_of_view_info = view_utils.find_and_apply_light_and_view_changes_for_moving_object(obj, game, oldpos)
    orddat.append(['game', 'light_changes', light_level_changes, obj.map_section])
    dict_of_char_view_info = {}
    charidlist = game.charnamesid.values()
    for objectid in dict_of_view_info:
        if objectid in charidlist:
            dict_of_char_view_info[objectid] = dict_of_view_info[objectid]
    orddat.append(['game', 'new_viewed_tiles', dict_of_char_view_info])
    mover_vis_changes = check_for_vis_changes_to_moving_object(obj,game)
    if mover_vis_changes['otherteam_now_vis'] or mover_vis_changes['otherteam_now_invis'] \
    or mover_vis_changes['obj_now_vis'] or mover_vis_changes['obj_now_invis']:
        obj.apply_vis_changes(**mover_vis_changes)
        if obj.objtype == 'playerchar':
            orddat.append([obj.id, 'mover_vis_changes', mover_vis_changes])
            
    nonmover_vis_changes = find_others_vis_changes_of_this_mobj_id(obj.id, game, stealth_move)
    view_utils.apply_others_vis_changes_of_mobj_id(obj.id, nonmover_vis_changes, game)
#    nonmover_vis_changes =  view_utils.check_for_and_apply_vis_changes_of_nonmoving_object(obj, game)
    if nonmover_vis_changes[0] or nonmover_vis_changes[1]:
        if obj.objtype == 'monster':
            orddat.append([obj.id, 'others_vis_changes_of_mobj', nonmover_vis_changes])
    
    return mover_vis_changes, nonmover_vis_changes

def determine_vis_of_enemy_id_list(perceiver_id, enemy_id_list, game, reason = ''):
    actual_otherteam_new_vis = set()
    perceiver = game.objectIdDict[perceiver_id]
    for id in enemy_id_list:
        enemy = game.objectIdDict[id]
        accurate = perception_check_see_enemy(perceiver, enemy, game, reason)
        if accurate:
            actual_otherteam_new_vis.add(id)
    return actual_otherteam_new_vis

def check_for_vis_changes_to_moving_object(mo, game):
#    total_otherteam_vis = set()
#    total_obj_vis = set()
    obj_vis_changes = {}
    enemy_ids, nonmobj_ids = view_utils.find_all_potentially_vis_objects_for_this_id(mo.id,game)
    
    potential_otherteam_new_vis = enemy_ids - mo.visible_otherteam_ids
    actual_otherteam_new_vis = determine_vis_of_enemy_id_list(mo.id, potential_otherteam_new_vis, game, reason = 'perceiver move')
    
#    obj_vis_changes['otherteam_now_vis'] = enemy_ids - mo.visible_otherteam_ids
    obj_vis_changes['otherteam_now_vis'] = actual_otherteam_new_vis
    obj_vis_changes['otherteam_now_invis'] = mo.visible_otherteam_ids - enemy_ids
    
    obj_vis_changes['obj_now_vis'] = nonmobj_ids - mo.visible_object_ids
    obj_vis_changes['obj_now_invis'] = mo.visible_object_ids - nonmobj_ids
    
    return obj_vis_changes 

def find_others_vis_changes_of_this_mobj_id(this_id, game, stealth_move = False):
    others_gaining_vis = set()
    others_losing_vis = set()
    this_obj = game.objectIdDict[this_id]
    if this_obj.objtype != 'playerchar' and this_obj.objtype != 'monster':
        return others_gaining_vis, others_losing_vis

    potential_viewer_ids, non_viewer_ids = view_utils.find_other_ids_potential_sight_of_this_id(this_id, game)
    if stealth_move:
        thisreason = 'enemy stealth move'
    else:
        thisreason = 'enemy move'
    
    for id in potential_viewer_ids:
        obj = game.objectIdDict[id]
        if this_id not in obj.visible_otherteam_ids:
            otherteam_new_vis = determine_vis_of_enemy_id_list(id, [this_id], game, reason = thisreason)
            if otherteam_new_vis:
                others_gaining_vis.add(id)
#                obj.apply_vis_changes(otherteam_now_vis = set([this_id]))
    for id in non_viewer_ids:
        obj = game.objectIdDict[id]
        if this_id in obj.visible_otherteam_ids:
            others_losing_vis.add(id)
#            obj.apply_vis_changes(otherteam_now_invis = set([this_id]))
    return (others_gaining_vis, others_losing_vis)
            
def find_others_vis_changes_of_this_nonmobj_id(this_id, game, remove_vis = False):
    # remove_vis used if, for example, item is picked up
    others_gaining_vis = set()
    others_losing_vis = set()
    this_obj = game.objectIdDict[this_id]
    if this_obj.objtype == 'playerchar' or this_obj.objtype == 'monster':
        return others_gaining_vis, others_losing_vis

    potential_viewer_ids, non_viewer_ids = view_utils.find_other_ids_potential_sight_of_this_id(this_id, game)
    
    if not remove_vis:
        for id in potential_viewer_ids:
            obj = game.objectIdDict[id]
            if this_id not in obj.visible_object_ids:
                others_gaining_vis.add(id)
    #            obj.apply_vis_changes(obj_now_vis = set([this_id]))
        for id in non_viewer_ids:
            obj = game.objectIdDict[id]
            if this_id in obj.visible_object_ids:
                others_losing_vis.add(id)
    #            obj.apply_vis_changes(obj_now_invis = set([this_id]))
    else:
        for id in potential_viewer_ids:
            obj = game.objectIdDict[id]
            if this_id in obj.visible_object_ids:
                others_losing_vis.add(id)
    #            obj.apply_vis_changes(obj_now_vis = set([this_id]))
        for id in non_viewer_ids:
            obj = game.objectIdDict[id]
            if this_id in obj.visible_object_ids:
                others_losing_vis.add(id)
    #            obj.apply_vis_changes(obj_now_invis = set([this_id]))
        
    return (others_gaining_vis, others_losing_vis)

def execute_move(obj, nextsq, game, event_time, stealth_move = False):

    print 'hgc, execute_move', obj.name, nextsq
    oldpos = obj.pos
    obj.setPosition(nextsq)
    obj.SetLastOrderedPos(nextsq)
    obj.popPath(game)

    mover_vis_changes, nonmover_vis_changes = vis_and_light_changes_from_move(obj, game, oldpos, stealth_move = stealth_move)

    if (obj.objtype == 'playerchar' and mover_vis_changes['otherteam_now_vis']) \
    or (obj.objtype == 'monster' and nonmover_vis_changes[0]):
        game.new_move_mode = 'phased'
        
    
    map_section_name = obj.map_section
    enc_ord = game.encounter_class.check_effect(['pos', map_section_name, nextsq, [obj.objtype, obj.name]])
    timed_eorddat = process_encounter_order(enc_ord, game)
    other_timed_event_list.extend(timed_eorddat)
    
    obj.check_triggered_effects('move', game)        

    evaluate_next_order(obj, game, event_time)

def cast_spell(source, spell_data, game, event_time):
    orddat = hctp_orddat[np]
    spell_name = source['spell_name']
    spell = game.complete_dict_of_spells[spell_name]
    caster_id = source['obj_id']
    caster = game.objectIdDict[caster_id]
    orddats = spell.effect(source,spell_data,game)
    orddat.extend(orddats)
    orddat.append([caster_id, 'pop0', caster.orders[0]])
    caster.pop_order(0)
    caster.check_triggered_effects('cast spell', game, source)        
    evaluate_next_order(caster, game, event_time)
    
#def call_func(obj,other_data,orddat,game):
def call_func(source,func_str,other_data, game):
    if 'spell_name' in source:
        this_class = game.complete_dict_of_spells[source['spell_name']]
        
    if this_class:
        func = getattr(this_class, func_str)
        if hasattr(func, '__call__'):
            func(other_data, game)
        
    
def remove_effect(obj, details):
    obj.remove_temporary_effect(details)
    
#def remove_bonus(obj, details):
#    obj.remove_bonus(details)
    
    
def premature_loss_of_effect(obj, details):
    orddat = hctp_orddat[np]
    remove_effect(obj, details)
    orddat.append([obj.id, 'effect lost', details])
    idx_to_remove = None
    for idx, timed_event_entry in enumerate(effects_timed_event_list):
#        event_time = timed_event_entry[1]
        timed_event = timed_event_entry[2]
        obj_id = timed_event[0]
        event_type = timed_event[1]
        effect_details = timed_event[2]
        if event_type == 'effect_expiring':
            if obj_id == obj.id:
                if effect_details == details:
                    idx_to_remove = idx
                    break
    if idx_to_remove != None:
        effects_timed_event_list.pop(idx_to_remove)
    

def schedule_free_move(obj, nextsq, game, use_time):
    time_required = find_time_to_next_move(game,obj,nextsq)
    event_time = use_time + time_required
    orders_timed_event_list.append((obj.subphase, event_time, [obj.id, 'move', nextsq, obj.pos]))

def schedule_spell_cast(obj, source, data, game, use_time):
    spell_name = source['spell_name']
    time_required = determine_casting_time(game,obj,spell_name)
    event_time = use_time + time_required
    orders_timed_event_list.append((obj.subphase, event_time, [obj.id, 'cast_spell', source, data]))

def schedule_standard_attack(obj, attacked_obj_id, source, game, use_time):
    time_required = return_standard_action_time()
    event_time = use_time + time_required
    orders_timed_event_list.append((obj.subphase, event_time, [obj.id, 'standard_attack', attacked_obj_id, source]))

def schedule_drop_item(obj, item, use_move_action, game, use_time):
    if use_move_action:
        time_required = return_move_action_time()
    else:
        time_required = 1
    event_time = use_time + time_required
    orders_timed_event_list.append((obj.subphase, event_time, [obj.id, 'drop item', item.id]))
    
def schedule_pickup_item(obj, item, use_move_action, game, use_time):
    if use_move_action:
        time_required = return_move_action_time()
    else:
        time_required = 1
    event_time = use_time + time_required
    orders_timed_event_list.append((obj.subphase, event_time, [obj.id, 'pickup item', item.id]))
    
def evaluate_next_order(obj, game, use_time = None, need_to_send_orddat = False):
    # if this function is called with an existing orddat, then there
    # will be some other way to send results back to clients.
    # if this function is called without an orddat, then this function
    # must send the data back to clients.
    
    if need_to_send_orddat:
        del hctp_orddat[:]
        hctp_orddat.append([])
        global np
        np = 0
        orddat = hctp_orddat[0]
    else:
        orddat = hctp_orddat[np]
    if use_time == None:
        use_time = game.Time
    action_scheduled = False
    orders = obj.orders
    while not action_scheduled:
        if orders:
            next_ord = orders[0]
            if next_ord:
                ord_type = next_ord[0]
                if ord_type == 'move':
                    path = next_ord[1]
                    action_scheduled = evaluate_proposed_move(obj, path[0], game, use_time)
                elif ord_type == 'cast_spell':
                    source = next_ord[1]
                    data = next_ord[2]
                    action_scheduled = evaluate_spellcast_order(obj, source, data, game, use_time)
                elif ord_type == 'standard_attack':
                    attacked_obj_id = next_ord[1]
                    source = next_ord[2]
                    action_scheduled = evaluate_standard_attack_order(obj, attacked_obj_id, source, game, use_time)
                elif ord_type == 'move to target id':
                    target_id = next_ord[1]
                    action_scheduled = evaluate_move_to_target_id(obj,target_id,game,use_time)
                elif ord_type == 'drop item':
                    item_id = next_ord[1]
                    use_move_action = next_ord[2]
                    action_scheduled = evaluate_drop_item(obj,item_id,use_move_action,game,use_time)
                elif ord_type == 'pickup item':
                    item_id = next_ord[1]
                    use_move_action = next_ord[2]
                    action_scheduled = evaluate_pickup_item(obj,item_id,use_move_action,game,use_time)
                    
                if not action_scheduled:
                    orddat.append([obj.id, 'pop0', obj.orders[0]])
                    orders.pop(0)
        else:
            action_scheduled = True
                
    # feedback from scheduling the event, such as a notification
    # that a spellcast has begun                
    if need_to_send_orddat and orddat and game.move_mode == 'free':  
        ev = HostSendDataEvent('free_move_results',orddat)
        queue.put(ev)
        

def evaluate_standard_attack_order(obj, attacked_obj_id, source, game, use_time):
    # only on hostcomplete
    
    # check for things preventing attack (paralysis, etc.)
    attack_allowed = True     # nothing preventing attack
    if attack_allowed:
        schedule_standard_attack(obj, attacked_obj_id, source, game, use_time)
#        orddat.append( [obj.id, 'begin attack', attacked_obj_id, melee_or_range, source])
    return attack_allowed
    

def evaluate_spellcast_order(obj, source, data, game, use_time):
    # only on hostcomplete
    
    # check for things preventing spellcast (paralysis, etc.)
    orddat = hctp_orddat[np]
    cast_allowed = True     # nothing preventing cast
    if cast_allowed:
        schedule_spell_cast(obj, source, data, game, use_time)
        orddat.append( [obj.id, 'begin spellcast', source, data])
    return cast_allowed
    
def evaluate_proposed_move(obj, next_sq, game, use_time):
    # only on hostcomplete
    
    # check for invisible but 'substantial' (blocking) monsters on nextsq
    # or being stuck in a trap, or paralysis, etc.
    move_allowed = True     # nothing preventing move
    if move_allowed:
        schedule_free_move(obj, next_sq, game, use_time)
    return move_allowed
            
def evaluate_move_to_target_id(obj, target_id, game, use_time):
    # only on hostcomplete
    
    # check for invisible but 'substantial' (blocking) monsters on nextsq
    # or being stuck in a trap, or paralysis, etc.
    orddat = hctp_orddat[np]
    move_allowed = True     # nothing preventing move
    if move_allowed:
        target = game.objectIdDict[target_id]
        if view_utils.los_between_two_tiles(obj.pos, target.pos, obj.map_section, game, reason = {'obj_id':obj.id}):
            path, cost = aStar(obj.pos, target.pos, obj, game, obj.map_section, move_adjacent = True)        
            new_ords = ['move', path]
            obj.orders.append(new_ords)
            ord = [obj.id, 'append new order', deepcopy(new_ords)]
            orddat.append(ord)
#            return False
    return False

def evaluate_drop_item(obj,item_id,use_move_action,game,use_time):
    item = game.objectIdDict[item_id]
    if obj.can_drop_item(item,game):
        schedule_drop_item(obj, item, use_move_action,game, use_time)
        return True
    else:
        return False
        
def evaluate_pickup_item(obj,item_id,use_move_action,game,use_time):
    item = game.objectIdDict[item_id]
    if obj.can_pickup_item(item,game):
        schedule_pickup_item(obj, item, use_move_action, game, use_time)
        return True
    else:
        return False
        
def process_encounter_order(enc_ord, game):
    timed_eorddat = []
    if enc_ord:
        try:
            ord_type = enc_ord[0]
        except TypeError:
            ev = ShowDefaultInfoPopupEvent("Encounter order isn't a list.")
            queue.put(ev)
        except: 
            ev = ShowDefaultInfoPopupEvent('Unexpected order returned from encounter class: ' + sys.exc_info()[0])
            queue.put(ev)
        else:
            if ord_type == 'change move mode':
                try:
                    new_mode = enc_ord[1]
                except IndexError:
                    ev = ShowDefaultInfoPopupEvent("Change move mode order from encounter doesn't \
                                                    specify new mode as 2nd item in list.")
                    queue.put(ev)
                except:
                    ev = ShowDefaultInfoPopupEvent('Unexpected order returned from encounter class: ' + sys.exc_info()[0])
                    queue.put(ev)
                else:
                    if new_mode == 'phased' or new_mode == 'free':
                        game.new_move_mode = new_mode
    return timed_eorddat

def calc_exp_for_kill(obj):
    return 100

def calc_damage_dice(obj, enemy_obj, source, game):
    # add str bonus, two hand, offhand, bow str effect, etc. here
    
    # output of this will be a list where each element is:
    #    a 4 element list where:
    #        the first element is number of rolls
    #        the second element is damage range
    #        the third element is bonus
    #        the fourth element is damage type

    if 'weapon_id' in source:
        weapon_id = source['weapon_id']
        weapon = game.objectIdDict[weapon_id]
        dmg_spec_list = weapon.melee_damage
    elif 'natural_attack' in source:
        natural_attack_name = source['natural_attack']
        dmg_spec_list = obj.natural_attacks[natural_attack_name][2]
    elif 'attack_hands' in source and source['attack_hands'] == 'unarmed':
        dmg_spec_list = [ ['1d3', 'bludgeon'] ]
    else:
        dmg_spec_list = []  # todo - should this default to unarmed attack?
    
    damage_dice = []
    if 'attack_type' in source:
        attack_type = source['attack_type']
        if attack_type == 'melee':
            for dmg_spec in dmg_spec_list:
                dmg_dice = dmg_spec[0]
                dmg_type = dmg_spec[1]
                dmg_details_list = parse_damage_string(dmg_dice)
                if dmg_type in ('bludgeon','slash','pierce'):
                    bonus = calc_melee_damage_bonus(self, enemy_obj, game, source)
                    dmg_details_list[2] += bonus
                dmg_details_list.append(dmg_type)
                
                damage_dice.append(dmg_details_list)
    return damage_dice

def roll_for_damage(damage_details_list, enemy_obj, damage_details, game):
    dam_tot = []
    damage_rolls = []
    damage_type = []
    damage_avoided = []
    for damage_spec in damage_details_list:
        temp_dam_tot = 0
        damage_spec_rolls = []
        num_rolls = damage_spec[0]
        die_range = damage_spec[1]
        extra = damage_spec[2]
        type = damage_spec[3]
        for rollnum in range(num_rolls):
            die_roll = random.randint(die_range[0],die_range[1])
            damage_spec_rolls.append(die_roll)
            temp_dam_tot += die_roll
            temp_dam_tot += extra
        dam_change, change_method = enemy_obj.modify_damage_received(temp_dam_tot, type, game) 
        temp_dam_tot += dam_change
        dam_tot.append(temp_dam_tot)
        damage_rolls.append(damage_spec_rolls)
        damage_type.append(type)
        damage_avoided.append([dam_change, change_method])

    # each of the following is a list where each element
    # is for one of the damage_specs in damage_details_list
    damage_details['damage_rolls'] = damage_rolls   # each element is a list of die rolls
    damage_details['damage_total'] = dam_tot    # each element is the total damage
    damage_details['damage_type'] = damage_type
    damage_details['damage_avoided'] = damage_avoided # each element is a 2 element list [dam_change, change_method]
        
def execute_attack(mo, enemy_obj, tohit_bonus, miss_chance, damage_details_list, armor_class, game, source):
    tohit_roll = random.randint(1,20)
    tohit_total = tohit_roll + tohit_bonus
    damage_details = {}
    damage_details['enemy_id'] = enemy_obj.id
    damage_details['tohit_roll'] = tohit_roll
    damage_details['tohit_bonus'] = tohit_bonus
    if miss_chance > 0.001:
        miss_chance_roll = random.random()
        damage_details['miss_chance'] = miss_chance
        damage_details['miss_chance_roll'] = miss_chance_roll
    else:
        miss_chance_roll = 0.0 
    if tohit_total >= armor_class and miss_chance_roll < miss_chance:
        result = 'damage_dealt'
        roll_for_damage(damage_details_list, enemy_obj, damage_details, game)
    else:
        result = 'miss'
        
    resolve_effects_from_attack(result, damage_details, mo, enemy_obj, game, source)

def resolve_effects_from_attack(result, damage_details, mo, enemy_obj, game, source):
    orddat = hctp_orddat[np]
    if result == 'miss':
        orddat.append([mo.id, 'missed attack on enemy', damage_details])
        orddat.append([enemy_obj.id, 'enemy missed attack', mo.id])
    else:
        dam_tot_list = damage_details['damage_total']
        dam_tot = 0
        for dam in dam_tot_list:
            dam_tot += dam
        enemy_obj.change_damage(dam_tot)
        msg = ''
        if enemy_obj.find_current_hit_points() <= 0:
            enemy_obj.eval_low_hp()
            if 'dead' in enemy_obj.status:
                msg = 'dead'
            elif 'dying' in enemy_obj.status:
                msg = 'dying'
            elif 'disabled' in enemy_obj.status:
                msg = 'disabled'
            elif 'broken' in enemy_obj.status:
                msg = 'broken'
            elif 'ruined' in enemy_obj.status:
                msg = 'ruined'
        damage_details['msg'] = msg
        orddat.append([mo.id, 'damage dealt', damage_details])
        orddat.append([enemy_obj.id, 'received damage', damage_details])
        
        if msg == 'dead':
            if mo.objtype == 'playerchar':
                new_exp = calc_exp_for_kill(enemy_obj)
                exp_dict = game.distribute_exp_among_party(new_exp)
                game.assign_exp_to_party_members(exp_dict)
                orddat.append(['game', 'assign exp', exp_dict])

            ids_that_see = view_utils.find_mobj_ids_that_see_this_id(enemy_obj.id, game)
            view_utils.remove_id_from_other_vis_lists(enemy_obj.id, ids_that_see, game)
            orddat.append(['game','lose vis of id', enemy_obj.id, ids_that_see]) 
            orddat.append([enemy_obj.id, 'dead', mo.id])
            
            new_ground_items = game.mobj_dies(enemy_obj)
            # todo - send new ground items to clients
            game.del_obj(enemy_obj)
            
        if enemy_obj.objtype == 'playerchar':
            # if dead, dying, unconscious, etc, remove view
            pass
        
    mo.check_triggered_effects('attack', game, source)        
    enemy_obj.check_triggered_effects('attacked', game, source)        
        
    if game.move_mode == 'free':
        if (mo.objtype == 'playerchar' and enemy_obj.objtype == 'monster') \
        or (mo.objtype == 'monster' and enemy_obj.objtype == 'playerchar'):
            game.new_move_mode == 'phased'

def made_saving_throw(thrower_id, throw_type, DC, reason_for_throw, game):
    orddat = hctp_orddat[np]
    thrower = game.objectIdDict[thrower_id]
    if throw_type == 'will':
        temp_bonus = thrower.find_total_effect_bonus(('saving_throw','will'), game, reason_for_throw)
        bonus = thrower.saving_throw_will + temp_bonus
    elif throw_type == 'reflex':
        temp_bonus = thrower.find_total_effect_bonus(('saving_throw','reflex'), game, reason_for_throw)
        bonus = thrower.saving_throw_reflex + temp_bonus
    if throw_type == 'fortitude':
        temp_bonus = thrower.find_total_effect_bonus(('saving_throw','fortitude'), game, reason_for_throw)
        bonus = thrower.saving_throw_fortitude + temp_bonus
        
    saving_roll = random.randint(1,20)
    total_saving_roll = bonus + saving_roll
    
    if saving_roll == 1:
        saved = False
    elif saving_roll == 20:
        saved = True
    elif total_saving_roll >= DC:
        saved = True
    else:
        saved = False
        
    saving_details = {}
    saving_details['reason_for_throw'] = reason_for_throw
    saving_details['DC'] = DC
    saving_details['die_roll'] = saving_roll
    saving_details['total_bonus'] = bonus
    saving_details['result'] = saved
    saving_details['throw_type'] = throw_type
    orddat.append([thrower_id, 'attempted saving throw', saving_details])
    if 'obj_id' in reason_for_throw:
        orddat.append([reason_for_throw['obj_id'], 'forced enemy saving throw', saving_details])
        
        
    print '################## hgc, saving throw ################', saving_details
    
    return saved

def passed_spell_resistance(caster,target,spell,reason_for_check,game):
    orddat = hctp_orddat[np]
    passed = True
    
    sr_effects = target.return_all_relevant_effect_bonuses('spell_resistance', game, reason_for_check)
    max_sr = 0
    for effect in sr_effects:
        if effect[1] > max_sr:
            max_sr = effect[1]
    max_sr = max(max_sr,target.spell_resistance)
    
    if max_sr > 0:
        passed = False
        cl = spell.find_caster_level(caster)
        roll = random.randint(1,20)
        checkval = roll + cl
        if checkval >= max_sr:
            passed = True
        sr_details = {}
        sr_details['reason_for_check'] = reason_for_check
        sr_details['spell resistance value'] = max_sr
        sr_details['die_roll'] = roll
        sr_details['caster_level'] = cl
        sr_details['result'] = passed
        orddat.append([target.id, 'attempted spell resistance', sr_details])
        if 'obj_id' in reason_for_check:
            orddat.append([reason_for_check['obj_id'], 'forced enemy spell resistance check', sr_details])
    return passed        

def find_perception_see_enemy_dc_bonus(perceiver, enemy, game, reason_for_check):
    bonus = 0
    map_section_name = perceiver.map_section
    
    # distance mod
    px = perceiver.pos[0]
    py = perceiver.pos[1]
    ex = enemy.pos[0]
    ey = enemy.pos[1]
    dist = sqrt( (px-ex)**2 + (py-ey)**2 )
    bonus += int(floor(dist/2.))
    
    # in melee mod, consider being in threatened square of enemy as being distracted
    if perceiver.objtype == 'playerchar':
        idlist = game.map_data[map_section_name]['monsters']
    elif perceiver.objtype == 'monster':
        idlist = []
        for id in game.charnamesid.values():
            obj = game.objectIdDict[id]
            if obj.map_section == map_section_name:
                idlist.append(id)
    for id in idlist:
        obj = game.objectIdDict[id]
        if perceiver.pos in obj.threatened_tiles(game):
            bonus += 5
            break

    # consider dim light as unfavorable, bright light as favorable
    light_data = game.map_data[map_section_name]['light']
    if light_data != 'uniform':
        enemy_light_level = light_data[enemy.pos]
        if enemy_light_level <= DIM_LIGHT_INTENSITY:
            bonus += 2
        elif enemy_light_level >= BRIGHT_LIGHT_INTENSITY:
            bonus -= 2
            
    return bonus
    

def perception_check_see_enemy(perceiver, enemy, game, type_of_check):
    # should only come here if enemy isn't already visible
    # will be opposed by stealth check only when enemy is in cover or concealment (not total), 
    # and even then only under 2 circumstances:
    #  enemy is making a stealthy move
    #  perceiver is moving
    orddat = hctp_orddat[np]
    accurate_knowledge = False
    map_section_name = perceiver.map_section
    if enemy.map_section == map_section_name:
        opposed_by_stealth_check = False
        reason_for_perc_check = {'obj_id':enemy.id,'reason':[type_of_check]}
        if type_of_check == 'enemy stealth move' or type_of_check == 'perceiver move':
            map_section = game.map[map_section_name]
            if enemy.pos in findAdjTiles(perceiver.pos[0], perceiver.pos[1], map_section):
                ranged_cover = False
            else:
                ranged_cover = True
            cover, soft_cover = view_utils.cover_between_two_tiles(perceiver.pos, enemy.pos, map_section_name, game, ranged = ranged_cover, reason = reason_for_perc_check)
            conceal_bonus = enemy.find_concealment_bonus(perceiver, game)
            if cover or conceal_bonus > 0:
                if not enemy.stealth_already_checked or not ranged_cover:
                    opposed_by_stealth_check = True
                    enemy.stealth_already_checked = True
            
        dc = 0
        dc_change = find_perception_see_enemy_dc_bonus(perceiver, enemy, game, reason_for_perc_check)
        dc += dc_change
        
        p_bonus = perceiver.find_total_effect_bonus(('skill','perception'), game, reason_for_perc_check)
        
        if opposed_by_stealth_check:
            reason_for_stealth_check = {'obj_id':perceiver.id,'reason':[type_of_check]}
            s_bonus = enemy.find_total_effect_bonus(('skill','stealth'), game, reason_for_stealth_check)
            if enemy.orders_summary['move_points_used_move_action'] > enemy.basemovespeed/2 \
            or enemy.orders_summary['move_points_used_standard_action'] > enemy.basemovespeed/2:
                s_bonus -= 5
            stealth_roll = random.randint(1,20)
            opposing_number = stealth_roll + s_bonus
        else:
            opposing_number = dc
        
        perception_roll = random.randint(1,20)
        if perception_roll + p_bonus >= opposing_number:
            accurate_knowledge = True
            
        perception_data = {}
        perception_data['reason_for_check'] = reason_for_perc_check
        perception_data['DC'] = dc
        perception_data['die_roll'] = perception_roll
        perception_data['total_bonus'] = p_bonus
        perception_data['result'] = accurate_knowledge
        
        print '############### hgc, perception check ###############', perception_data
        
        stealth_data = {}
        if opposed_by_stealth_check:
            stealth_data['reason_for_check'] = reason_for_stealth_check
            stealth_data['die_roll'] = stealth_roll
            stealth_data['total_bonus'] = s_bonus
            stealth_data['result'] = accurate_knowledge
             
        orddat.append([perceiver.id, 'did perception check', perception_data, stealth_data])
        if opposed_by_stealth_check:
            orddat.append([enemy.id, 'did stealth check to oppose perception', stealth_data])
    
    return accurate_knowledge

            
def find_timed_events_occurring(timed_event_list, max_time, subphase = -1, move_mode = 'phased'): 
    '''
    Generally there are two event timing systems when it comes to calculations made by the host.
    One system handles orders for each mobile object, and the other handles 'effects'.  The orders
    system events occur during the subphase (the mobjs 'turn'), and the effects events occur either 
    just before or just after a sides (or mobjs) turn.
    
    For the orders system, a mobj puts an order into its orders list.  This order is placed into the 
    hostcomplete's (hosts copy of game) order list for that mobj.  If game.move_mode == 'free', and
    the mobj had no previous orders, then this order is 'evaluated' immediately.  If game.move_mode
    == 'phased', then this order will be evaluated during that mobjs subphase.
    
    Evaluating an order means to determine if it can be executed, and then to 'schedule' an event.
    Scheduling an orders event means to put an event into orders_timed_event_list.
    
    At the appropriate time, a scheduled event is 'executed', which means to carry out the event
    on hostcomplete, and tell all the clients the result.  When an orders event is executed, the 
    final step is to evaluate the next order in the mobj's orders list.
    
    So the sequence is:
        - order created and transmitted to hostcomplete
        - order evaluated
        - event(s) scheduled on hostcomplete
        - scheduled event executed on hostcomplete
            - results sent back to clients
            - next order for mobj evaluated
    
    Events allowed in orders_timed_event_list are 'move','cast_spell','standard_attack','drop item', etc.
    
    For the effects system, the event is placed into effects_timed_event_list directly.  This occurs 
    on host_complete and will always be a result of some orders event.  If game.move_mode == 'free',
    the effect will be executed at the appropriate time.  If game.move_mode == 'phased', then
    the effect will be scheduled to occur either just before or just after a mobjs subphase, although
    the time will be just to determine just which pre- or post- subphase is used.  In other words,
    an effect uses 2 completely different systems to determine when it occurs, depending on
    game.move_mode.
    
    Currently, events allowed in effects_timed_event_list can't be the same as ones allowed in
    orders_timed_event_list since execution of these events doesn't call for the next order
    to be evaluated.
    Events allowed in effects_timed_event_list are 'effect_expiring','forced drop item', etc.
    
    Structure of an event entry in timed_event_lists:
    (subphase, execution time, event details)
    
    Structure of event details:
    [object_id, event type, anything else]
    
    '''
    
    timed_events_occurring = []
    highest_idx = -1
    if move_mode == 'free':     # don't care about subphase, timed_event_list is sorted entirely based on time
        for idx, event_entry in enumerate(timed_event_list):
            if event_entry[1] <= max_time:
                timed_event = event_entry
                timed_events_occurring.append(timed_event)
                highest_idx = idx
            else:
                break
        timed_event_list[0:highest_idx+1] = []
    elif move_mode == 'phased':     # only return events in proper subphase.  timed_event_list is
                                    # sorted first based on subphase, then on time
        first_subphase_event_found = False
        first_subphase_idx = 0
        for idx, event_entry in enumerate(timed_event_list):
            if event_entry[0] == subphase:
                if not first_subphase_event_found:
                    first_subphase_event_found = True
                    first_subphase_idx = idx
                if event_entry[1] <= max_time:
                    timed_event = event_entry
                    timed_events_occurring.append(timed_event)
                    highest_idx = idx
                else:
                    break
        timed_event_list[first_subphase_idx:highest_idx+1] = []
        
    return timed_events_occurring

def handle_game_timed_events(timed_events, game):
    # host complete only
    
    orddat = hctp_orddat[np]
    for timed_event_entry in timed_events:
        event_time = timed_event_entry[1]
        timed_event = timed_event_entry[2]
        event_type = timed_event[1]
        if event_type == 'set time':
            game.set_time(timed_event[2])
            orddat.append(['game', 'set time', timed_event[2]])
        elif event_type == 'move':
            obj_id = timed_event[0]
            next_sq = timed_event[2]
            obj = game.objectIdDict[obj_id]
            orddat.append(timed_event)
            execute_move(obj, next_sq, game, event_time)
        elif event_type == 'cast_spell':
#            obj_id = timed_event[0]
            source = timed_event[2]
            data = timed_event[3]
#            obj = game.objectIdDict[obj_id]
            orddat.append(timed_event)
            cast_spell(source, data, game, event_time)
        elif event_type == 'standard_attack':
            obj_id = timed_event[0]
            attacked_obj_id = timed_event[2]
            source = timed_event[3]
            obj = game.objectIdDict[obj_id]
            orddat.append(timed_event)
            do_standard_attack(obj, attacked_obj_id, source, game, event_time)
        elif event_type == 'drop item':
            obj_id = timed_event[0]
            item_id = timed_event[2]
            obj = game.objectIdDict[obj_id]
            item = game.objectIdDict[item_id]
            orddat.append(timed_event)
            do_drop_item(obj, item, game, event_time)
        elif event_type == 'forced drop item':
            obj_id = timed_event[0]
            item_id = timed_event[2]
            obj = game.objectIdDict[obj_id]
            item = game.objectIdDict[item_id]
            orddat.append(timed_event)
            forced_drop_item(obj, item, game, event_time)
        elif event_type == 'pickup item':
            obj_id = timed_event[0]
            item_id = timed_event[2]
            obj = game.objectIdDict[obj_id]
            item = game.objectIdDict[item_id]
            orddat.append(timed_event)
            do_pickup_item(obj, item, game, event_time)
        elif event_type == 'effect_expiring':
            obj_id = timed_event[0]
            details = timed_event[2]
            obj = game.objectIdDict[obj_id]
            orddat.append(timed_event)
            remove_effect(obj, details)
        elif event_type == 'client call function':
            obj_id = timed_event[0]
            other_data = timed_event[2]
            orddat.append([obj_id, 'client call func', other_data])
#        elif event_type == 'client call function blocking':
#            obj_id = timed_event[0]
#            other_data = timed_event[2]
#            orddat.append([obj_id, 'client call func blocking', other_data])
        elif event_type == 'create orddat entry':
            obj_id = timed_event[0]
            orddat_entry = timed_event[2]
            orddat.append(orddat_entry)
            
#            obj = game.objectIdDict[obj_id]
#            call_func(obj, other_data, orddat, game)
#        elif event_type == 'bonus_expiring':
#            obj_id = timed_event[0]
#            details = timed_event[2]
#            obj = game.objectIdDict[obj_id]
#            orddat.append(timed_event)
#            remove_bonus(obj, details)

    if game.new_move_mode == 'phased':
        if game.move_mode == 'free':
            game.move_mode = 'phased'
            game.new_move_mode = None
            orddat.append(['game','change to phased mode'])
        
        
def generate_events_during_time_advance(next_time, game):
    orddat = hctp_orddat[np]
    game.ai.order_all_moves()
    
    if next_time - game.last_updated_encounter_time > 2.:
        game.last_updated_encounter_time = next_time
        enc_ord = game.encounter_class.check_effect(['time', next_time])
        timed_eorddat = process_encounter_order(enc_ord, game)
        other_timed_event_list.extend(timed_eorddat)

def clear_free_move_orders(game):
    
    del orders_timed_event_list[:]
    
    game.saveandload.restoreSave('hostcomplete')
    idlist = game.charnamesid.values()
    for id in idlist:
        playerchar = game.objectIdDict[id]
        playerchar.set_new_orders(None, game)
    for section_name in game.map_section_names:
        for mid in game.map_data[section_name]['monsters']:
            mon = game.objectIdDict[mid]
            mon.set_new_orders(None, game)
    game.saveandload.restoreSave('player')
        
    for id in idlist:
        ev = HostSendDataEvent('set_new_orders_after_order_deletion',[id,None])
        queue.put(ev)
    
def clear_existing_timed_orders_for_id(id, game):
    # for clearing stale timed events from order list.
    # used in phased mode when setting new orders
    obj = game.objectIdDict[id]
    entries_to_remove = []
    for event_entry in orders_timed_event_list:
        timed_event = event_entry[2]
        event_obj_id = timed_event[0]
        if id == event_obj_id:
            entries_to_remove.append(event_entry)
    for entry in entries_to_remove:
        orders_timed_event_list.remove(entry)
    
def summarize_orders(id, game):
    obj = game.objectIdDict[id]
    ssa_idx = len(obj.orders)
    for oidx,ord in enumerate(obj.orders):
        ordtype = ord[0]
        if ordtype == 'move action for standard action':
            ssa_idx = oidx
            break

    move_action_used = False
    standard_action_used = False
    swift_action_used = False
    move_points_used_move_action = 0
    move_points_used_standard_action = 0
    
    lop = obj.pos
    for oidx in range(ssa_idx):
        ord = obj.orders[oidx]
        ord_type = ord[0]
        if ord_type == 'move':
            final_pos = ord[1][-1]
            allowed, cost = eval_free_move_to_tile(obj, lop, final_pos, game)
            if allowed:
                move_points_used_move_action += cost
                move_action_used = True
            lop = final_pos
        elif ord_type == 'cast_spell':
            standard_action_used = True
        elif ord_type == 'standard_attack':
            standard_action_used = True
        elif ord_type == 'move to target id':
            pass
        elif ord_type == 'drop item':
            pass
        elif ord_type == 'pickup item':
            pass
        elif ordtype == 'move action for standard action':
            pass

    if ssa_idx != len(obj.orders):      # any further orders must mean that move action was used
                                        # in place of standard action
        for oidx in range(ssa_idx, len(obj.orders)):
            ord = obj.orders[oidx]
            ord_type = ord[0]
            if ord_type == 'move':
                final_pos = ord[1][-1]
                allowed, cost = eval_free_move_to_tile(lop, final_pos, game)
                if allowed:
                    move_points_used_standard_action += cost
                    standard_action_used = True
                lop = final_pos
            elif ord_type == 'cast_spell':
                pass
            elif ord_type == 'standard_attack':
                pass
            elif ord_type == 'move to target id':
                pass
            elif ord_type == 'drop item':
                pass
            elif ord_type == 'pickup item':
                pass
            elif ordtype == 'move action for standard action':
                pass
        

    orders_summary_dict = {}
    orders_summary_dict['move_action_used'] = move_action_used 
    orders_summary_dict['standard_action_used'] = standard_action_used
    orders_summary_dict['swift_action_used'] = swift_action_used
    orders_summary_dict['move_points_used_move_action'] = move_points_used_move_action
    orders_summary_dict['move_points_used_standard_action'] = move_points_used_standard_action
    
    return orders_summary_dict

#def allow_append_order(obj, order, game):
#    # not sure when host wouldn't allow an order to be appended, since
#    # client should generally be kept informed of basic stuff such as when
#    # a standard action is allowed and only let a standard action order
#    # be sent to host if it's allowed, but here's the function anyways
#    return True
#        
#def allow_delete_order(obj, order, game):
#    return True
    

