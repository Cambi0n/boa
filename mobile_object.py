import game_object as gobj
from userconstants import *
from gamefunctions import *
import view_utils

class MobileObject(gobj.GameObject):
    def __init__(self, **params):
        params.setdefault('can_contain_items', True)
        params.setdefault('items',{})
        gobj.GameObject.__init__(self,**params)

        params.setdefault('has_vision',True)
        self.has_vision = params['has_vision']
        params.setdefault('vision_type','normal')
        self.vision_type = params['vision_type']
        params.setdefault('visible_otherteam_ids',set())
        self.visible_otherteam_ids = params['visible_otherteam_ids']
        params.setdefault('visible_object_ids',set())
        self.visible_object_ids = params['visible_object_ids']
        params.setdefault('languages_understood',[])
        self.languages_understood = params['languages_understood']
        params.setdefault('languages_spoken',[])
        self.languages_spoken = params['languages_spoken']
        params.setdefault('breathes',True)
        self.breathes = params['breathes']
        params.setdefault('eats',True)
        self.eats = params['eats']
        params.setdefault('sleeps',True)
        self.sleeps = params['sleeps']
        params.setdefault('natural_reach',1)    # in tiles
        self.natural_reach = params['natural_reach']
        
        params.setdefault('natural_attacks',{})
        self.natural_attacks = params['natural_attacks']    # a dict where key is a string of attack name 'claw', etc
                                                            # and value is a list where:
                                                            # 1st item is the number of attacks of this type allowed in a full attack
                                                            # 2nd item is attack bonus
                                                            # 3rd item is a list of damage specs, 
                                                            #    where each damage spec is a 2 element list:
                                                            #        1st item is damage dice
                                                            #        2nd item is damage type
                                                            # 4th item (optional) is anything special that happens with 
                                                            #    successful attack (disease, etc.)
#        params.setdefault('perception_bonus',0)
#        self.perception_bonus = params['perception_bonus']
                                                            

        self.other_movable_objects = []     # other movable objects associated with this char, 
                                            # like pets, familiars, spell objects, etc.

        
        self.lastOrderedMapSection = None
        self.lastOrderedPos = None
        
        self.target = None
        self.cost_to_target = 0.
        
        self.orders = []
        self.ordertimes = []
        self.subphase = 0
        self.orders_summary = {}
        self.orders_summary['move_action_used'] = False 
        self.orders_summary['standard_action_used'] = False
        self.orders_summary['swift_action_used'] = False
        self.orders_summary['move_points_used_move_action'] = 0
        self.orders_summary['move_points_used_standard_action'] = 0
        
        self.stealth_already_checked = False

        self.basemovespeed = gameBaseMoveSpeed            # squares per round
        self.movespeed = self.basemovespeed    # current movespeed 
        self.move_points_remaining = self.movespeed
        self.move_points_remaining_after_last_order = self.movespeed
        self.move_points_remaining_standard_action = self.movespeed
        self.move_points_remaining_after_last_order_standard_action = self.movespeed
        self.residual_move_pulses = 0.
        self.nextsq = None             # for partial progress to next square.  Partial progress is lost
                                        # if a new order demands a new next square
        self.next_move_time = 0.
        
        self.str = 10
        self.dex = 10
        self.int = 10
        self.con = 10
        self.wis = 10
        self.cha = 10
        
        self.current_energy = 0.
        self.energy_needed = -1
        self.current_energy_ord = None    # the order for which energy is being accumulated
        
        self.allowed_move_tiles = set()
        self.allowed_move_tiles_fresh = False
        
        self.action_mode = 'move'   # either 'move' or 'standard'
        self.actions_used = []      # possible values to be added to list are 'standard', 'move', 'swift', 
                                    # 'full', 'partial_move', 'partial_standard', and 'five_foot'
                                    # 'partial_move' would generally be converted to 'move' if a standard
                                    # action is performed after the partial move.  There may be feats that
                                    # allow the use of the rest of the movement points after a standard
                                    # action (i.e. partial move, attack, completion of move)
                                    # 'partial_standard' applies if using move for a standard action
        self.actions_used_sequence = [] # each order in self.orders is one of: 'standard','move','partial_move',
                                        # 'swift','full','partial_standard','five_foot','free'.  Some, such as 'partial_move',
                                        # might show up multiple times.
                                    
#        self.base_energy_per_pulse = gameEnergyPerPulse 
#        self.energy_per_pulse = self.base_energy_per_pulse 
#        self.energy_per_pulse = gameEnergyPerPulse      # this might change if say have a ring of speed
   
#    def setPosition(self, pos, game, spforceadjust = False):
#        # overrides game_obect setPosition
#        if self.pos != pos:
#            self.pos = pos
#            find_all_viewed_tiles_for_adventurer(adv, vinfo, map_section, game)   
        self.normal_viewed_tiles = set()     
        self.dim_viewed_tiles = set()     
        
        self.before_order_decisions = []
        self.concentration_data = None
        
    def add_before_order_decision(self, data):
        self.before_order_decisions.append(data)
        
    def update_viewed_tiles(self, normal_viewed_tiles_set, dim_viewed_tiles_set):
        print 'mobj, update1', id(self.normal_viewed_tiles)
        self.normal_viewed_tiles.clear()
        self.normal_viewed_tiles.update(normal_viewed_tiles_set)
        self.dim_viewed_tiles.clear()
        self.dim_viewed_tiles.update(dim_viewed_tiles_set)
        print 'mobj, update2', id(self.normal_viewed_tiles)
#        self.normal_viewed_tiles = normal_viewed_tiles_set
#        self.dim_viewed_tiles = dim_viewed_tiles_set
#        self.viewed_tiles = find_one_objects_viewed_tiles_within_radius(self, game)                

    def set_all_visible_objects(self, otherteam_set, nonmobj_set):
        self.visible_otherteam_ids = otherteam_set
        self.visible_object_ids = nonmobj_set

    def apply_vis_changes(self, **obj_vis_changes):
        self.visible_otherteam_ids |= obj_vis_changes.get('otherteam_now_vis',set())
        self.visible_otherteam_ids -= obj_vis_changes.get('otherteam_now_invis',set())
        self.visible_object_ids |= obj_vis_changes.get('obj_now_vis',set())
        self.visible_object_ids -= obj_vis_changes.get('obj_now_invis',set())
#    def apply_vis_changes(self, obj_vis_changes):
#        self.visible_otherteam_ids |= obj_vis_changes[0]
#        self.visible_otherteam_ids -= obj_vis_changes[1]
#        self.visible_object_ids |= obj_vis_changes[2]
#        self.visible_object_ids -= obj_vis_changes[3]
   
    def reverse_vis_changes(self, **obj_vis_changes):
        self.visible_otherteam_ids -= obj_vis_changes.get('otherteam_now_vis',set())
        self.visible_otherteam_ids |= obj_vis_changes.get('otherteam_now_invis',set())
        self.visible_object_ids -= obj_vis_changes.get('obj_now_vis',set())
        self.visible_object_ids |= obj_vis_changes.get('obj_now_invis',set())
#    def reverse_vis_changes(self, obj_vis_changes):
#        self.visible_otherteam_ids -= obj_vis_changes[0]
#        self.visible_otherteam_ids |= obj_vis_changes[1]
#        self.visible_object_ids -= obj_vis_changes[2]
#        self.visible_object_ids |= obj_vis_changes[3]
   
    def popPath(self, game):
        print 'in mobj, popping', self.orders
        if self.orders:
            if self.orders[0][0] == 'move':
                print 'in mobj, popping2', self.orders[0], id(self.orders[0])
                path = self.orders[0][1]
                path.pop(0)
                if not self.orders[0][1]: # no more path
                    self.pop_order(0)
                 
            elif self.orders[0][0] == 'pursue target':
                if self.pathtotarget:
                    path = self.pathtotarget
                    path.pop(0)

    def unPopPath(self, pos, game):
        print 'in mobj, unpopping', self.orders
        if len(self.orders) == 0:
            self.orders.append(['move',[]])
        if self.orders[0][0] != 'move':
            self.orders.insert(0,['move',[]])
#        if self.orders:
#            if self.orders[0][0] == 'move':
        print 'in mobj, unpopping2', self.orders[0], id(self.orders[0])
        self.orders[0][1].insert(0,pos)
                
    def append_order(self, ord, game = None):
        self.orders.append(ord)
        if ord[0] == 'move':
            self.allowed_move_tiles_fresh = False
        elif ord[0] == 'standard_attack':
            self.allowed_move_tiles_fresh = False
        elif ord[0] == 'cast_spell':
            self.allowed_move_tiles_fresh = False
            
    def delete_last_order_phased(self):
        if len(self.orders) != 0:
            self.orders.pop()
            
            
#            needsnewlop = False
#            lastord = self.orders[-1]
#            if lastord[0] == 'move':
#                needsnewlop = True
#            
#            self.orders.pop()
#            
#            if needsnewlop:
#                if len(self.orders) == 0:
#                    self.lastOrderedPos = self.pos
#                else:
#                    newlopfound = False
#                    for uord in reversed(self.orders):
#                        if uord[0] == 'move':
#                            self.lastOrderedPos = uord[1][-1]
#                            newlopfound = True
#                            break
#                    if not newlopfound:
#                        self.lastOrderedPos = self.pos
#
#            self.recalc_movement_points_remaining(self)
#            self.update_actions_used('remove_last_order')
#            self.allowed_move_tiles_fresh = False
#            self.find_allowed_moves_for_mobj(game, 'last_ordered')

    def delete_last_order_free_move_mode(self):
        # should be used only on host complete
        if len(self.orders) > 1:
            self.orders.pop()
        elif len(self.orders) == 1:
            if self.orders[0][0] == 'move':
                path = self.orders[0][1]
                newpath = path[0]
                self.orders = [['move',[newpath]]]

    def pop_order(self, listnum):
        print 'mobj, pop_order', self.orders
        if self.orders:
            num_items = len(self.orders)
            if listnum < num_items:
                print 'mobj, pop_order2', id(self.orders[0])
                self.orders.pop(listnum)

    def insert_order(self, ord, loc):
        print 'mobj, insert_order', self.orders, ord, loc, id(ord)
        self.orders.insert(loc, ord)
                
    def set_new_orders(self, newords, game):
        print 'mobj, set new orders', self.orders, newords, id(newords), self.objtype
        self.orders = []
        if newords:
            self.orders = newords
            lop = self.find_last_ordered_pos()
            self.SetLastOrderedPos(lop)
        else:
            self.SetLastOrderedPos(self.pos)
        # change following to recreate the actions used list from the orders list
        self.recalc_movement_points_remaining(game)
        self.allowed_move_tiles_fresh = False
        self.find_allowed_moves_for_mobj(game, 'last_ordered')
            

    def SetLastOrderedMapSection(self, mapsection, game = None):
        self.lastOrderedMapSection = mapsection
        
    def SetLastOrderedPos(self, pos, game = None):
        self.lastOrderedPos = pos
        
    def find_last_ordered_pos(self):
        pos = self.pos
        for ord in self.orders:
            if ord[0] == 'move':
                pos = ord[1][-1]
        return pos
    
#    def findLastOrderedMode(self, whichmode):
#        lastmode = self.mode[whichmode]
#        for ord in self.orders:
#            if ord[0] == 'changemode' and ord[1] == whichmode:
#                lastmode = ord[2]
#        return lastmode
#    
#    def findModeAfterOrdNum(self, whichmode, ordnum = None):
#        mode = self.mode[whichmode]
#        for idx, ord in enumerate(self.orders):
#            if idx <= ordnum or ordnum == None:
#                if ord[0] == 'changemode' and ord[1] == whichmode:
#                    mode = ord[2]
#            else:
#                break
#        return mode
#        
#    def findCurrentMode(self, whichmode, game = None):
#        return self.findModeAfterOrdNum(whichmode, ordnum = -1)    
            
#    def setStealth(self, stealthmode, searchmode):
#        self.stealth = self.calcStealth(stealthmode, searchmode)
#        
#    def calcStealth(self, stealthmode, searchmode):
#        return self.basestealth * StealthSettings[self.subtype][stealthmode][0] * SearchSettings[self.subtype][searchmode][0]
#
#    def setSearching(self, stealthmode, searchmode):
#        self.searching = self.calcSearching(stealthmode, searchmode)
#        
#    def calcSearching(self, stealthmode, searchmode):
#        return self.basesearching * StealthSettings[self.subtype][stealthmode][2] * SearchSettings[self.subtype][searchmode][2]
    
    def order_use_of_movement_points(self, mp_spent):
        if mp_spent > self.move_points_remaining_after_last_order:
            self.move_points_remaining_after_last_order = 0
        else:
            self.move_points_remaining_after_last_order -= mp_spent
        
    def set_movement_points_remaining_after_last_order(self, new_mp):
        self.move_points_remaining_after_last_order = new_mp
        
    def set_current_energy(self, newenergy):
        self.current_energy = newenergy
    
    def set_energy_needed(self, newenergy):
        self.energy_needed = newenergy
    
    def set_current_energy_ord(self, newenergy_ord):
        self.current_energy_ord = newenergy_ord
        
    def update_actions_used(self,change):
        if change == 'use_partial_move_action':
            self.actions_used_sequence.append('partial_move')
            if self.move_points_remaining_after_last_order < 1.:
                if 'partial_move' in self.actions_used:
                    self.actions_used.remove('partial_move') 
                self.actions_used.append('move')
            else:
                if 'partial_move' not in self.actions_used and 'move' not in self.actions_used:
                    self.actions_used.append('partial_move')
        elif change == 'use_standard_action':
            self.actions_used_sequence.append('standard')
            self.actions_used.append('standard')
            if 'partial_move' in self.actions_used:
                self.actions_used.remove('partial_move') 
                self.actions_used.append('move')
        elif change == 'use_move_action':
            self.actions_used_sequence.append('move')
            self.actions_used.append('move')
        elif change == 'use_full_round':
            self.actions_used_sequence.append('full')
            self.actions_used.append('full')
            
        elif change == 'clear all':
            self.actions_used = []
            self.actions_used_sequence = []
                    
        elif change == 'remove_last_order':
            if self.actions_used_sequence != []:
                last_action = self.actions_used_sequence[-1]
                self.actions_used_sequence.pop()
                if last_action == 'partial_move':
                    if 'move' in self.actions_used:
                        self.actions_used.remove('move')
                        self.actions_used.append('partial_move')
                    if 'partial_move' not in self.actions_used_sequence and 'move' not in self.actions_used_sequence \
                    and 'partial_move' in self.actions_used:
                        self.actions_used.remove('partial_move')
                elif last_action == 'move':
                    self.actions_used.remove('move')
                elif last_action == 'standard':
                    self.actions_used.remove('standard')
                    if 'move' in self.actions_used:
                        if self.move_points_remaining_after_last_order >= 1.:
                            self.actions_used.remove('move')
                            self.actions_used.append('partial_move')
                elif last_action == 'full':
                    self.actions_used.remove('full')
                        
                    
    def change_action_mode(self,new_mode):
        if self.action_mode != new_mode:
            self.action_mode = new_mode
    
#    def changeUnitMode(self, mode, newval):
#        
#        if mode == 'stealth':
#            oldval = self.mode['stealth']
#            self.mode['stealth'] = newval
#            self.setStealth(newval, self.mode['searching'])
#            self.setSearching(newval, self.mode['searching'])
#        elif mode == 'searching':
#            oldval = self.mode['searching']
#            self.mode['searching'] = newval
#            self.setStealth(self.mode['stealth'], newval)
#            self.setSearching(self.mode['stealth'], newval)
#            
#        return oldval

    def find_allowed_moves_for_mobj(self, game, type = 'current'):
        if not self.allowed_move_tiles_fresh:
            if 'move' not in self.actions_used \
            and not self.five_foot_ordered():
                if type == 'last_ordered':
                    am = find_allowed_moves(self.lastOrderedPos, self, self.move_points_remaining_after_last_order, game)
                elif type == 'current':
                    am = find_allowed_moves(self.pos, self, self.move_points_remaining_after_last_order, game)
                    
                self.allowed_move_tiles = am
            else:
                self.allowed_move_tiles = set()
            self.allowed_move_tiles_fresh = True
            
    def set_residual_move_pulses(self, residual):
        self.residual_move_pulses = residual

    def cleanup_after_done_button(self):
        self.allowed_move_tiles = []
        self.allowed_move_tiles_fresh = True
        
    def refresh_at_round_start(self, game):
        # this function won't be called by hostcomplete.
        # it is called in clientroundresults, after processing entire round
        # interface issues need to be reset here.  Game related issues that the
        # host also needs to know about should be reset in hostgamecalcs,
        # reset_obj 
        self.move_points_remaining = self.find_movespeed(game)
        self.move_points_remaining_after_last_order = self.move_points_remaining 
        self.move_points_remaining_standard_action = self.move_points_remaining
        self.move_points_remaining_after_last_order_standard_action = self.move_points_remaining 
        if self.can_choose_orders(game, {}):
            self.allowed_move_tiles_fresh = False
            self.find_allowed_moves_for_mobj(game, 'current')
        else:
            self.allowed_move_tiles = set()
  
#    def calc_armor_class(self, mo, source = None):
#        # can put in calculations based on size, flat foot, 
#        # dodge, equip, dex, etc.
#        return self.armor_class
        

    def find_allowed_drop_slots(self, item):
        # todo - do I need to do this on host? I don't think so, it
        # would make the inventory page sluggish.  Better to give
        # client sufficient information to make decision.
        allowed_slots = []
        for slot in item.allowed_slots:
            # do various checks for class, attribute, status restrictions
            # also don't allow moving storage item to storage
            allowed_slots.append(slot)
        
        if item != self.items['storage']:
            allowed_slots.append('backpack')
            
        return allowed_slots
    
    def set_target(self, target_id):
        self.target = target_id
            
        
    def find_allowed_actions(self):
        if self.can_take_actions():
            allowed_act = set(['full','standard','move','partial_move','partial_standard', \
                               'five_foot','swift'])
            
            if 'full' in self.actions_used or not self.can_do_full_action():
                allowed_act -= set(['full','standard','move','partial_move','partial_standard'])
                
            if 'standard' in self.actions_used or not self.can_do_standard_action():
                allowed_act -= set(['full','standard','partial_standard'])
                
            if 'move' in self.actions_used or not self.can_do_move_action():
                allowed_act -= set(['full','move', 'partial_move'])
                    
            if 'partial_standard' in self.actions_used:
                allowed_act -= set(['full','standard'])
    
            if 'partial_move' in self.actions_used:
                allowed_act -= set(['full','move'])
    
            if 'five_foot' in self.actions_used \
            or not self.five_foot_allowed():
                allowed_act -= set(['five_foot'])
    
            if 'swift' in self.actions_used:
                allowed_act -= set(['swift'])
        else:
            allowed_act = set()
            
        return allowed_act

    def five_foot_allowed(self):
        allowed = True
        for ord in self.orders:
            if ord[0] == 'move':
                allowed = False
            elif ord[0] == 'five_foot':
                allowed = False
        return allowed
    
    def five_foot_ordered(self):
        ordered = False
        for ord in self.orders:
            if ord[0] == 'five_foot':
                ordered = True
        return ordered
    
    def set_next_move_time(self,next_sq,game):
         time_req = find_time_to_next_move(game,self,next_sq)
         self.next_move_time = game.Time + time_req

    def eval_low_hp(self):
        # overridden by adventurer.py
        if self.find_current_hit_points() <= 0:
            self.status.add('dead')
        else:
            self.status -= set(['dead'])

    def modify_damage_received(self, damage_tot, damage_type, game):
        # for resistances, etc.
        return 0,None
        
    def find_ability_bonus(self,ability,game=None):
#        extra_bonus = 0
        if ability == 'str':
            bonus = self.find_total_effect_bonus(('str'), game)
            val = self.str + bonus
#            extra_bonus = self.find_total_temporary_effect_bonus(('ability_check','str'), game)
        elif ability == 'dex':
            bonus = self.find_total_effect_bonus(('dex'), game)
            val = self.dex + bonus
#            extra_bonus = self.find_total_temporary_effect_bonus(('ability_check','dex'), game)
        elif ability == 'int':
            bonus = self.find_total_effect_bonus(('int'), game)
            val = self.int + bonus
#            extra_bonus = self.find_total_temporary_effect_bonus(('ability_check','int'), game)
        elif ability == 'con':
            bonus = self.find_total_effect_bonus(('con'), game)
            val = self.con + bonus
#            extra_bonus = self.find_total_temporary_effect_bonus(('ability_check','con'), game)
        elif ability == 'wis':
            bonus = self.find_total_effect_bonus(('wis'), game)
            val = self.wis + bonus
#            extra_bonus = self.find_total_temporary_effect_bonus(('ability_check','wis'), game)
        elif ability == 'cha':
            bonus = self.find_total_effect_bonus(('cha'), game)
            val = self.cha + bonus
#            extra_bonus = self.find_total_temporary_effect_bonus(('ability_check','cha'), game)
        return ability_bonus(val)

    def can_choose_orders(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_choose_orders', game, reason_for_check)
        
    def can_take_actions(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_take_actions', game, reason_for_check)
        
    def can_do_move_action(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_do_move_action', game, reason_for_check)

    def can_do_standard_action(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_do_standard_action', game, reason_for_check)

    def can_do_full_action(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_do_full_action', game, reason_for_check)

    def can_do_free_actions(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_do_free_actions', game, reason_for_check)

    def can_drop_item(self,item,game):
        can_drop = True
        if not self.can_choose_orders(game) or not self.can_do_free_actions(game):
            can_drop = False
        elif game.move_mode == 'phased':
            can_drop = False
            if self.can_take_actions():
                loc = self.find_loc_of_item(item)
                if loc == 'stored':
                    if 'move' in self.find_allowed_actions():
                        can_drop = True
                else:
                    can_drop = True
        return can_drop
    
    def can_pickup_item(self,item,game):
        can_pickup = True
        if not self.can_choose_orders(game) or not self.can_do_free_actions(game):
            can_pickup = False
        elif game.move_mode == 'phased':
            can_pickup = False
            if self.can_take_actions():
                if 'move' in self.find_allowed_actions():
                    can_pickup = True
        return can_pickup
    
    def is_fleeing(self, game = None, reason_for_check = {}):
        return not self.find_total_effect_binary('not_fleeing', game, reason_for_check)
    
    def is_sleeping(self, game = None, reason_for_check = {}):
        return not self.find_total_effect_binary('not_sleeping', game, reason_for_check)
    
#    def is_stealthed(self, game = None, reason_for_check = {}):
#        return not self.find_total_effect_binary('not_stealthy', game, reason_for_check)
    
    def can_speak(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_speak', game, reason_for_check)
        
    def can_hear(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_hear', game, reason_for_check)
    
    def can_understand_all_languages(self, game = None, reason_for_check = {}):
        return not self.find_total_effect_binary('cant_understand_all_languages', game, reason_for_check)
        
    def can_speak_all_languages(self, game = None, reason_for_check = {}):
        return not self.find_total_effect_binary('cant_speak_all_languages', game, reason_for_check)

    def can_do_cast_somatics(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_do_cast_somatics', game, reason_for_check)

    def can_see(self, game = None, reason_for_check = {}):
        return self.find_total_effect_binary('can_see', game, reason_for_check)

    def obj_potentially_seeable(self, obj, game = None, reason_for_check = {}):
        i_can_see_obj = False
        if self.can_see(game, reason_for_check):
            obj_invis = False
            if obj.is_invisible(game, reason_for_check):
                obj_invis = True
            elif self.__class__.__name__ == 'MonsterClass':
                if self.monster_type == 'undead':
                    reason_for_check['obj_id'] = self.id
                    if obj.is_invisible_to_undead(game, reason_for_check):
                        obj_invis = True
                        
            if not obj_invis:
                if obj.pos in self.normal_viewed_tiles \
                or obj.pos in self.dim_viewed_tiles:
                    i_can_see_obj = True
        
        return i_can_see_obj

    def drop_item(self,item,game):
        map_section_name = self.map_section
        self.remove_item_no_loc(item)
        item.setPosition(self.pos)
        item.set_map_section(map_section_name)
        game.map_data[map_section_name]['objects'].add(item.id)
        
    def pickup_item(self,item,game):
        map_section_name = self.map_section
        self.add_item(item,'storage',None)
#        self.remove_item_no_loc(item)
#        item.setPosition(self.pos)
#        item.set_map_section(map_section_name)
        game.map_data[map_section_name]['objects'].remove(item.id)
        
    def find_flee_effect_entry(self,game = None):
        flee_entry = None
        for effect_entry in self.temporary_effects:
            if effect_entry[0][0] == 'Frightened':
                flee_entry = effect_entry
                break
            elif effect_entry[0][0] == 'Command(Flee)':
                flee_entry = effect_entry
                break
        return flee_entry   
    
    def find_movespeed(self,game=None, reason_for_check = None):
        mult = self.find_total_effect_mult('movespeed', game, reason_for_check)
        actual_movespeed = int(self.movespeed * mult)
        bonus = self.find_total_effect_bonus('movespeed', game, reason_for_check)
        if bonus:
            actual_movespeed += bonus
        print '************** mob obj, find movespeed ************', actual_movespeed, mult, bonus
        return actual_movespeed
        
    def add_spell_concentration_data(self,conc_data):
        self.concentration_data = conc_data
        
    def calc_miss_chance(self, attacker, game, source):
        bonuses = self.return_all_relevant_effect_bonuses('miss chance', game, source)
        c_bonuses = find_concealment_bonus(self, attacker, game)
        bonuses.extend(c_bonuses)
#        if self.pos in attacker.dim_viewed_tiles:
#            bonuses.append(['concealment', 20.])
#        elif self.pos not in attacker.normal_viewed_tiles:
#            bonuses.append(['concealment', 50.])
#            
#        if self.pos in attacker.normal_viewed_tiles:
#            if self.pos in game.map_data['fog']:
#                bonuses.append(['concealment', 20.])

        # organize by type
        bonus_count = {}
        for bonus in bonuses:
            if bonus[0] not in bonus_count:
                bonus_count[bonus[0]] = []
            bonus_count[bonus[0]].append(bonus[1])
        
        # find biggest miss chance of each type
        max_bonuses = []
        for bonus_list in bonus_count.itervalues():
            max_bonus = 0
            for bonus in bonus_list:
                if bonus > max_bonus:
                    max_bonus = bonus
            max_bonuses.append(max_bonus)
            
        not_miss_chance = 1.0
        for bonus in max_bonuses:
            not_miss_chance *= (1. - bonus/100.)
            
        miss_chance = 1. - not_miss_chance
        
        return miss_chance      # a fraction between 0.0 and 1.0
        

    def threatened_tiles(self, game):
        map_section = game.map[self.map_section]
        reach_min, reach_max = self.find_reach_amt()
        tile_list = relativeTilesWithinRadius(reach_max)
        max_tile_set = set(absolutePosPlusRelativeTilelist(tile_list,self.pos,map_section))        
        tile_list = relativeTilesWithinRadius(reach_min)
        min_tile_set = set(absolutePosPlusRelativeTilelist(tile_list,self.pos,map_section))        
                        
        threatened_tiles = max_tile_set
        threatened_tiles -= min_tile_set
        if reach_min == 0:
            threatened_tiles.add(self.pos)
            
        remove_tile_set = set()
        for tile in threatened_tiles:
            if not is_tile_passable(tile,self.map_section,game):
                remove_tile_set.add(tile)
        for tile in remove_tile_set:
            threatened_tiles.remove(tile)
                
        return threatened_tiles

    def find_reach_amt(self):
        # todo - add code for whips, although I'm not sure it's worth the trouble.
        # Whips violate so many other rules (a melee attack that provokes AoO,
        # a reach weapon that can attack adjacent tiles, a 15' reach instead 
        # of doubling normal reach).
        
        using_reach_weapon = False
        using_only_reach_weapon = False
        if 'bothhands' in self.items:
            if self.items['bothhands']:
                bothhands_item = self.items['bothhands']
                if hasattr(bothhands_item,'reach'):
                    if bothhands_item.reach:
                        using_reach_weapon = True
                        using_only_reach_weapon = True
        if 'mainhand' in self.items:
            if self.items['mainhand']:
                mainhand_item = self.items['mainhand']
                if hasattr(mainhand_item,'reach'):
                    if mainhand_item.reach:
                        using_reach_weapon = True
                        using_only_reach_weapon = False
        if 'offhand' in self.items:
            if self.items['offhand']:
                offhand_item = self.items['offhand']
                if hasattr(offhand_item,'reach'):
                    if offhand_item.reach:
                        using_reach_weapon = True
                        using_only_reach_weapon = False
                    
        reach_min = 0
        reach_max = self.natural_reach
        
        if using_only_reach_weapon:
            reach_min = self.natural_reach  # a tile at reach_min distance is not attackable (unless reach_min = 0)
            reach_max = 2*self.natural_reach
        elif using_reach_weapon:
            reach_max = 2*self.natural_reach
            
        return reach_min, reach_max
        
    def recalc_movement_points_remaining(self, game):
        lop = self.pos
        mapsection = self.map_section
        totalcost = 0.
        for uo in self.orders:
            ordtype = uo[0]
            if ordtype == 'move':
                path = uo[1]
                for newdest in path:
                    newpath, cost = aStar(lop, newdest, self, game, mapsection)
                    lop = newdest
                    totalcost += cost
                    
        self.set_movement_points_remaining_after_last_order(self.find_movespeed(game) - totalcost)
    
        
                
#        ids_that_see = view_utils.find_mobj_ids_that_see_this_id(item.id, game)
#        view_utils.add_id_to_other_vis_lists(item.id, ids_that_see, game)             
#    def check_for_light(self):
#        for k,v in self.items.iteritems():
            
        
