
from copy import deepcopy
from userconstants import *
import view_utils

class GameObject():
    def __init__(self, **params):
#        params.setdefault('name',"")
#        self.name = params['name']
        
        params.setdefault('id',None)
        self.id = params['id']
        
        params.setdefault('type',[])  # are there objects with 2 types?
        self.type = params['type']
        params.setdefault('subtype',[])   # there are objects with multiple subtypes
        self.subtype = params['subtype']
        params.setdefault('subsubtype',None)
        self.subsubtype = params['subsubtype']

        params.setdefault('name','')
        self.name = params['name']
        params.setdefault('display_name','')
        self.display_name = params['display_name']
        params.setdefault('short_desc','')
        self.short_desc = params['short_desc']
        params.setdefault('long_desc','')
        self.long_desc = params['long_desc']
        params.setdefault('objtype',None)   # options are:
                                            # 'playerchar',
                                            # 'monster',
                                            # 'carried_item' (can be picked up)
                                            # 'fixed_item' (such as altar, pile of trash, etc.)
                                            # 'trap'
                                            # 'other_mobj' (such as flaming sphere, etc.)
        self.objtype = params['objtype']
        params.setdefault('alignment',[])   # usually two strings; e.g. ['lawful','good']
        self.alignment = params['alignment']
        
        params.setdefault('max_hit_points',1)
        self.max_hit_points = params['max_hit_points']
        params.setdefault('base_hit_points',1)      # hp from die rolls, without con bonus
        self.base_hit_points = params['base_hit_points']
        params.setdefault('num_hit_dice',1)
        self.num_hit_dice = params['num_hit_dice']
        params.setdefault('hit_die','1d6')
        self.hit_die = params['hit_die']
        params.setdefault('armor_class',10)
        self.armor_class = params['armor_class']
        params.setdefault('status',set())   #dead dying disabled for adventurers, broken ruined for carried items
        self.status = params['status']
        params.setdefault('saving_throw_will',0)
        self.saving_throw_will = params['saving_throw_will']
        params.setdefault('saving_throw_reflex',0)
        self.saving_throw_reflex = params['saving_throw_reflex']
        params.setdefault('saving_throw_fortitude',0)
        self.saving_throw_fortitude = params['saving_throw_fortitude']
        params.setdefault('spell_resistance',0)
        self.spell_resistance = params['spell_resistance']

        params.setdefault('map_section',None)
        self.map_section = params['map_section']
        params.setdefault('pos',None)
        self.pos = params['pos']

        params.setdefault('size',1)     # in squares
        self.size = params['size']
        params.setdefault('weight',0)
        self.weight = params['weight']
        params.setdefault('material',[])
        self.material = params['material']
        params.setdefault('value',0)
        self.value = params['value']
        
#        params.setdefault('visible',True)
#        self.visible = params['visible']


        params.setdefault('is_a_light',False)
        self.is_a_light = params['is_a_light']
        params.setdefault('is_showing_light',False)
        self.is_showing_light = params['is_showing_light']
        params.setdefault('bright_light_radius',-1)
        self.bright_light_radius = params['bright_light_radius']
#        params.setdefault('first_light_intensity',2)
#        self.first_light_intensity = params['first_light_intensity']
        params.setdefault('normal_light_radius',-1)
        self.normal_light_radius = params['normal_light_radius']
#        params.setdefault('second_light_intensity',1)
#        self.second_light_intensity = params['second_light_intensity']
        params.setdefault('dim_light_radius',-1)
        self.dim_light_radius = params['dim_light_radius']
        params.setdefault('ultradim_light_radius',-1)
        self.ultradim_light_radius = params['ultradim_light_radius']

        params.setdefault('allowed_slots',[])
        self.allowed_slots = params['allowed_slots']
        
#        params.setdefault('can_be_equipped_in_hands',False)
#        self.can_be_equipped_in_hands = params['can_be_equipped_in_hands']
#        params.setdefault('two_hands_required',False)
#        self.two_hands_required = params['two_hands_required']
        
        params.setdefault('can_be_picked_up',True)
        self.can_be_picked_up = params['can_be_picked_up']
        
        params.setdefault('can_contain_items', False)
        self.can_contain_items = params['can_contain_items']
        
        if self.can_contain_items:
            params.setdefault('items',[])
            self.items = params['items']
            if type(self.items) is dict:
                self.items['storage'] = None
                
        params.setdefault('temporary_effects',[])
        self.temporary_effects = params['temporary_effects']
        
        params.setdefault('item_effects',[])        # for things like armor bonus from armor
        self.item_effects = params['item_effects']
        
        params.setdefault('permanent_effects',[])   # for things like race where bonuses are sometimes
                                                    # conditional depending on reason for bonus
        self.permanent_effects = params['permanent_effects']
        
#        params.setdefault('items_with_effects',{})
#        self.items_with_effects = params['items_with_effects']    # so don't have to search all items for effects from items
                                            # for example, armor worn will have an entry here due to armor bonus    
                                            # key is id of item
                                            # value is a dict where possible keys are:
                                            #     'bonus', 'mult','binary'
                                            #     values of *this* dict are a list of functions associated with the item
        
        params.setdefault('allowed_target_locs',set())   # used for tile locations when view.target_mode == True
        self.allowed_target_locs = params['allowed_target_locs']
        
        params.setdefault('allowed_targets',set())   # used for target objects when view.target_mode == True
        self.allowed_targets = params['allowed_targets']

        self.damage_taken = 5

    def setPosition(self, pos):
        self.pos = pos

    def set_map_section(self, section, game = None, spforceadjust = False):
        self.map_section = section
        
    def list_items(self, listall = False):
        itemslist = []
        if hasattr(self,'items'):
            if type(self.items) is dict:
                looper = self.items.values()
            elif type(self.items) is list:
                looper = self.items
            for v in looper:
                if v:
                    itemslist.append(v)
                    if listall:
                        itemslist.extend(v.list_items(listall = listall))
        return itemslist
    
    def assign_id(self, id):
        self.id = id
        
    def change_damage(self, change):
        # if change is positive, that means object sustained damage
        if change > 0:
            for effect_entry in self.temporary_effects:
                effect_details = effect_entry[0]
                if effect_details[0] == 'Temporary Hit Points':
                    temp_hp = effect_details[3]
                    if temp_hp > 0:
                        if change > temp_hp:
                            change -= temp_hp
                            effect_details[3] = 0
                        else:
                            effect_details[3] -= change
                            change = 0
        if change:
            self.damage_taken += change
            if self.damage_taken < 0:
                self.damage_taken = 0
                
    def find_current_hit_points(self):
        current_max_hp = self.find_current_max_hp()
        current_hit_points = current_max_hp - self.damage_taken
        return current_hit_points
            
    def find_current_max_hp(self):
        ab = self.find_ability_bonus('con')
        other_hp = self.find_total_effect_bonus('hp')       
        hp = self.base_hit_points + ab*self.find_total_level() + other_hp
        return hp
        
    def find_total_temporary_hit_points(self):
        temp_hp = 0
        for effect_entry in self.temporary_effects:
            effect_details = effect_entry[0]
            if effect_details[0] == 'Temporary Hit Points':
                temp_hp += effect_details[3]
        return temp_hp
            
    def find_ability_bonus(self,ab):
        return 0
        
    def find_total_level(self):
        return self.num_hit_dice
    
    def eval_low_hp(self):
        if self.find_current_hit_points() <= find_current_max_hp()/2:
            self.status -= set(['ruined'])
            self.status.add('broken')
        elif self.find_current_hit_points() <= 0:
            self.status -= set(['broken'])
            self.status.add('ruined')
        else:
            self.status -= set(['broken','ruined'])
            
        return status
    
    def show_current_hp_description(self):
        if feedback_level == 0 or feedback_level == 1:
            if self.find_current_hit_points() <= 0:
                msg = 'dead'
            elif self.find_current_hit_points() < self.find_current_max_hp()/2:
                msg = 'unhealthy'
            else:
                msg = 'healthy'
        else:
            msg = str(self.find_current_hit_points()) + ' HP'
        return msg
        
    def set_extended_object_info(self,owner,game):
        '''
        
        raw_data is dictionary with 'text' and 'buttons' keys
        'text' has sequential keys.  Each of these has 'string',
        'color' (optional), and 'font' (optional).  The wordwrap
        function will be used to place this text.
        
        raw_data can also have 'text_panel_format' and 
        'button_panel_format' keys.  The values for these are
        dictionaries of format.
        
        'buttons' has sequential keys.  Each of these has 
        'contents' for value of button, and 'function'
        for function to call when pressing button.
        A special entry for 'function' is 'close' to
        close the popup.  Buttons can also have a
        'format' key.
        '''

        # todo - put extended info here
        data = {}
        data['name'] = self.name
        data['long_desc'] = self.long_desc    
        
        return data
        
#        raw_data['button_panel_format'] = {'background':(50,50,50,150)}
#        raw_data['buttons'] = {}
#        raw_data['buttons'][0] = {}
#        raw_data['buttons'][0]['contents'] = gui.Label('Ok')
#        raw_data['buttons'][0]['function'] = 'close'
        
        
    def remove_item(self,item,loc,slot):
        if self.can_contain_items:
            if loc == 'equipped':
                item.carried = False
                item.equipped = False
                self.items[slot] = None
                if hasattr(item,'effect_if_equipped'):
                    if item.effect_if_equipped:
                        self.remove_item_effects(item.id)
            elif loc == 'storage':
                if type(self.items) is dict:
                    storage = self.items['storage']
                    if hasattr(storage,'items'):    # should never fail, shouldn't be able to put
                                                    # item that can't store stuff into storage slot
                        if item in storage.items:
                            item.carried = False
                            storage.items.remove(item)
                            if hasattr(item,'effect_if_carried'):
                                if item.effect_if_carried:
                                    self.remove_item_effects(item.id)
                elif type(self.items) is list:
                    if item in self.items:
                        item.carried = False
                        self.items.remove(item)
                        if hasattr(item,'effect_if_carried'):
                            if item.effect_if_carried:
                                self.remove_item_effects(item.id)
                        
    def remove_item_no_loc(self, item):
        if self.can_contain_items:
            if type(self.items) is dict:
                for k,v in self.items.iteritems():
                    if k == 'storage':
                        if v == item:
                            item.carried = False
                            self.items[k] == None
                            if hasattr(item,'effect_if_carried'):
                                if item.effect_if_carried:
                                    self.remove_item_effects(item.id)
                        if hasattr(v,'items'):    # should never fail, shouldn't be able to put
                                                        # item that can't store stuff into storage slot
                            if item in v.items:
                                item.carried = False
                                v.items.remove(item)
                                if hasattr(item,'effect_if_carried'):
                                    if item.effect_if_carried:
                                        self.remove_item_effects(item.id)
                                break
                    else:
                        if v == item:
                            item.carried = False
                            self.items[k] = None
                            if hasattr(item,'effect_if_equipped'):
                                if item.effect_if_equipped:
                                    self.remove_item_effects(item.id)
                            break
            elif type(self.items) is list:
                if item in self.items:
                    item.carried = False
                    self.items.remove(item)
                    if hasattr(item,'effect_if_carried'):
                        if item.effect_if_carried:
                            self.remove_item_effects(item.id)
        
        
    def add_item(self, item, loc, slot):
        if self.can_contain_items:
            item.setPosition(self.pos)
            print 'game object, add_item', self, self.pos, item, item.id, item.pos
            if loc == 'equipped':
                item.carried = True
                item.equipped = True
                self.items[slot] = item
                if hasattr(item,'effect_if_equipped'):
                    if item.effect_if_equipped:
                        self.add_item_effects(item)
            elif loc == 'storage':
                item.carried = True
                if type(self.items) is dict:
                    storage = self.items['storage']
                    if hasattr(storage,'items'):
                        storage.items.append(item)
                elif type(self.items) is list:
                    self.items.append(item)
                if hasattr(item,'effect_if_carried'):
                    if item.effect_if_carried:
                        self.add_item_effects(item)
        
    def find_loc_of_item(self, item):
        return_loc = None
        if self.can_contain_items:
            if type(self.items) is dict:
                for k,v in self.items.iteritems():
                    if k == 'storage':
                        if v == item:
                            return_loc = 'storage'
                        elif hasattr(v,'items'):    # should never fail, shouldn't be able to put
                                                        # item that can't store stuff into storage slot
                            if item in v.items:
                                return_loc = 'stored'
                                break
                    else:
                        if v == item:
                            return_loc = k
                            break
            elif type(self.items) is list:
                if item in self.items:
                    return_loc = 'stored'
        return return_loc
    
    def calc_armor_class(self, attacking_obj = None, game = None, source = None):
        # can put in calculations based on size, flat foot, 
        ac = self.armor_class
        ac += self.find_total_effect_bonus('armor_class', game, source)        
        return ac 
    
    def add_temporary_effect(self, new_effect, game, effect_func_str_dict = {}, dispells = []):
        #new_effect = [name of effect, exp_time, source, variable_data]    variable data is optional
        # it can be used for something like temporary hit points, which is a bonus that changes, or it could
        # contain a list or a dictionary of data that the effect needs to keep track of and that might
        # change.  This data should be easily transferred over the network (no class refs).
        #bonus_callback is used to determine additions or subtractions to an attribute. A return of 0 is no change.
        #binary_callback is used to answer binary questions such as 'can_move', 'can_choose_orders'. 
        #  A return of True indicates no change from normal status. 
        #mult_callback is used to determine multiplicative changes to an attribute. A return of 1. is no change.
        #  The only thing mult applies to might be movement speed.
        #triggered callback is used for cases when the object with the effect does something to change
        #  the effect, such as attacking which removes Hide From Undead spell
        
        
        this_class = None
        source = new_effect[2]
        if 'spell_name' in source:
            this_class = game.complete_dict_of_spells[source['spell_name']]
            if dispells:
                entries_to_remove = []
                for idx,effect_entry in enumerate(self.temporary_effects):
                    if effect_entry[0][0] in dispells:
                         entries_to_remove.append(effect_entry)
                for entry in entries_to_remove:
                    try:
                        self.temporary_effects.remove(entry)
                    except ValueError:
                        pass
        elif 'condition_name' in source:
            this_class = game.dict_of_conditions[source['condition_name']]
            
        if this_class:
            effect_func_dict = {}
            if 'bonus' in effect_func_str_dict:
                for bonus_entry in effect_func_str_dict['bonus']:
                    bonus_func = getattr(this_class, bonus_entry)
                    if hasattr(bonus_func, '__call__'):
                        if 'bonus' not in effect_func_dict: 
                            effect_func_dict['bonus'] = []
                        effect_func_dict['bonus'].append(bonus_func)
            if 'mult' in effect_func_str_dict:
                for mult_entry in effect_func_str_dict['mult']:
                    mult_func = getattr(this_class, mult_entry)
                    if hasattr(mult_func, '__call__'):
                        if 'mult' not in effect_func_dict: 
                            effect_func_dict['mult'] = []
                        effect_func_dict['mult'].append(mult_func)
            if 'binary' in effect_func_str_dict:
                for binary_entry in effect_func_str_dict['binary']:
                    binary_func = getattr(this_class, binary_entry)
                    if hasattr(binary_func, '__call__'):
                        if 'binary' not in effect_func_dict: 
                            effect_func_dict['binary'] = []
                        effect_func_dict['binary'].append(binary_func)
            if 'triggered' in effect_func_str_dict:
                for triggered_entry in effect_func_str_dict['triggered']:
                    triggered_func = getattr(this_class, triggered_entry)
                    if hasattr(triggered_func, '__call__'):
                        if 'triggered' not in effect_func_dict: 
                            effect_func_dict['triggered'] = []
                        effect_func_dict['triggered'].append(triggered_func)
            
        if effect_func_dict:
            self.temporary_effects.append([new_effect, effect_func_dict])
        
        
    def add_permanent_effect(self, new_effect, game, effect_func_str_dict = {}):
        #new_effect = [name of effect, source, variable_data]    see add_temporary_effect for details on variable_data
        #bonus_callback is used to determine additions or subtractions to an attribute. A return of 0 is no change.
        #binary_callback is used to answer binary questions such as 'can_move', 'can_choose_orders'. 
        #  A return of True indicates no change from normal status. 
        #mult_callback is used to determine multiplicative changes to an attribute. A return of 1. is no change.
        #  The only thing mult applies to might be movement speed.
        #triggered callback is used for cases when the object with the effect does something to change
        #  the effect, such as attacking which removes Hide From Undead spell
        
        
        if len(new_effect) == 3:    # so variable_data is always 4th entry and source is always the
                                    # 3rd entry.  Permanent effects don't need
                                    # expiration time. (the normal 2nd entry).
            new_effect.append(deepcopy(new_effect[2]))
            new_effect[2] = deepcopy(new_effect[1])
            new_effect[1] = None
        this_class = None
        source = new_effect[1]
        if 'spell_name' in source:
            this_class = game.complete_dict_of_spells[source['spell_name']]
        elif 'condition_name' in source:
            this_class = game.dict_of_conditions[source['condition_name']]
        elif 'race_name' in source:
            this_class = game.dict_of_races[source['race_name']]
            
        if this_class:
            effect_func_dict = {}
            if 'bonus' in effect_func_str_dict:
                for bonus_entry in effect_func_str_dict['bonus']:
                    bonus_func = getattr(this_class, bonus_entry)
                    if hasattr(bonus_func, '__call__'):
                        if 'bonus' not in effect_func_dict: 
                            effect_func_dict['bonus'] = []
                        effect_func_dict['bonus'].append(bonus_func)
            if 'mult' in effect_func_str_dict:
                for mult_entry in effect_func_str_dict['mult']:
                    mult_func = getattr(this_class, mult_entry)
                    if hasattr(mult_func, '__call__'):
                        if 'mult' not in effect_func_dict: 
                            effect_func_dict['mult'] = []
                        effect_func_dict['mult'].append(mult_func)
            if 'binary' in effect_func_str_dict:
                for binary_entry in effect_func_str_dict['binary']:
                    binary_func = getattr(this_class, binary_entry)
                    if hasattr(binary_func, '__call__'):
                        if 'binary' not in effect_func_dict: 
                            effect_func_dict['binary'] = []
                        effect_func_dict['binary'].append(binary_func)
            if 'triggered' in effect_func_str_dict:
                for triggered_entry in effect_func_str_dict['triggered']:
                    triggered_func = getattr(this_class, triggered_entry)
                    if hasattr(triggered_func, '__call__'):
                        if 'triggered' not in effect_func_dict: 
                            effect_func_dict['triggered'] = []
                        effect_func_dict['triggered'].append(triggered_func)
            
        if effect_func_dict:
            self.permanent_effects.append([new_effect, effect_func_dict])
        
#        replace_idx = -1
#        dont_replace = False
#        for idx,effect in enumerate(self.temporary_effects):
#            if new_effect[0] == effect[0]:
#                if new_effect[1] > effect[1]:
#                    replace_idx = idx
#                    break
#                else:
#                    dont_replace = True
#                    break
#        if replace_idx != -1:
#            self.temporary_effects.pop(replace_idx)
#        if not dont_replace:
#            self.temporary_effects.append(new_effect)
            
    def remove_temporary_effect(self, effect_to_remove):
        #new_effect = [name, exp_time, source]
        remove_idx = -1
#        effect_to_remove = effect_entry_to_remove[0]
        for idx,effect_entry in enumerate(self.temporary_effects):
            effect = effect_entry[0]
            if effect_to_remove[0] == effect[0]:    # same name
                if effect_to_remove[1] == effect[1]:    # same expiration time
                    if effect_to_remove[2] == effect[2]:    # same source
                        remove_idx = idx
                        break
        if remove_idx != -1:
            self.temporary_effects.pop(remove_idx)


    def remove_item_effects(self, item_id):
        #new_effect = [name, exp_time, source]
        remove_idx = None
#        effect_to_remove = effect_entry_to_remove[0]
        for idx,effect_entry in enumerate(self.item_effects):
            effect_details = effect_entry[0]
            if item_id == effect_details[0]:    # same item id
                remove_idx = idx
                break
        if remove_idx:
            self.item_effects.pop(remove_idx)
            
#    def add_bonus(self, bonus_details):
#        # only add if new bonus lasts longer than identical existing bonus,
#        # or if no identical bonus already present
#        self.bonuses.append(bonus_details)
#            
#    def remove_bonus(self, bonus_details):
##        modified_attribute = bonus_details[0]
##        bonus_type, val, exp_time, source = bonus_details[1:]
##        bonus_to_remove = [bonus_type, val, exp_time, source]
#        remove_idx = -1
#        for idx,bonus in enumerate(self.bonuses):
#            if bonus == bonus_details:
#                remove_idx = idx
#                
#        if remove_idx != -1:
#            self.bonuses.pop(remove_idx)

    def add_item_effects(self, item):
        # effect details is [item_id]         not sure what else is needed yet
        effect_func_dict = {}
#        if hasattr(item,'effect_details') and item.effect_details:
        if hasattr(item,'effect_func_dict') and item.effect_func_dict:
#                effect_details = item.effect_details
            effect_func_str_dict = item.effect_func_dict
            if 'bonus' in effect_func_str_dict:
                for bonus_entry in effect_func_str_dict['bonus']:
                    bonus_func = getattr(item, bonus_entry)
                    if hasattr(bonus_func, '__call__'):
                        if 'bonus' not in effect_func_dict: 
                            effect_func_dict['bonus'] = []
                        effect_func_dict['bonus'].append(bonus_func)
            if 'mult' in effect_func_str_dict:
                for mult_entry in effect_func_str_dict['mult']:
                    mult_func = getattr(item, mult_entry)
                    if hasattr(mult_func, '__call__'):
                        if 'mult' not in effect_func_dict: 
                            effect_func_dict['mult'] = []
                        effect_func_dict['mult'].append(mult_func)
            if 'binary' in effect_func_str_dict:
                for binary_entry in effect_func_str_dict['binary']:
                    binary_func = getattr(item, binary_entry)
                    if hasattr(binary_func, '__call__'):
                        if 'binary' not in effect_func_dict: 
                            effect_func_dict['binary'] = []
                        effect_func_dict['binary'].append(binary_func)
            if effect_func_dict:
                self.item_effects.append([[item.id],effect_func_dict])
                

    def find_total_effect_bonus(self, value_being_checked, game = None, reason_for_check = None):
        # value being checked is a tuple.  It might have just one entry (e.g. ('tohit'), or ('str')) or it might have
        # 2 entries (e.g. ('saving throw','will') or ('skill','climb') or ('ability_bonus','str')
        # note that 'ability_bonus' (which affects the bonus, typically changes a die roll) is different 
        # than 'ability' (which affects ability level directly, i.e. +4 to str.
        
        # reason_for_check is a 'source' type of entry.  See spells.py for explanation of 'source' entries.
        total_bonus = 0
        bonuses = self.return_all_relevant_effect_bonuses(value_being_checked, game, reason_for_check)        
#        bonuses = []
#        if type(value_being_checked) is not tuple:
#            value_being_checked = (value_being_checked,)
#        for effect_entry in self.temporary_effects:
#            if 'bonus' in effect_entry[1]:
#                bonus_func_list = effect_entry[1]['bonus']
#                for bonus_func in bonus_func_list:
#                    bonus_data = bonus_func(effect_entry[0], self, game, value_being_checked = value_being_checked, reason_for_check = reason_for_check)
#                    if bonus_data:
#                        bonuses.append(bonus_data)
#        for effect_entry in self.item_effects:
#            if 'bonus' in effect_entry[1]:
#                bonus_func_list = effect_entry[1]['bonus']
#                for bonus_func in bonus_func_list:
#                    bonus_data = bonus_func(self, game, value_being_checked = value_being_checked, reason_for_check = reason_for_check)
#                    if bonus_data:
#                        bonuses.append(bonus_data)
                
        # compile dict with bonus types as key, size of bonuses in a list as value
        bonus_count = {}
        for bonus in bonuses:
            if bonus[0] not in bonus_count:
                bonus_count[bonus[0]] = []
            bonus_count[bonus[0]].append(bonus[1])
            
        for bonus_type,value_list in bonus_count.iteritems():
            this_bonus = -100000
            for value in value_list:
                if value > this_bonus:  # if multiple bonuses of same type, choose most positive one
                    this_bonus = value
            if this_bonus != -100000:
                total_bonus += this_bonus
            
        return total_bonus
        
    def find_total_effect_mult(self, value_being_checked, game = None, reason_for_check = None):
        # value being checked is a tuple.  It might have just one entry (e.g. ('tohit')) or it might have
        # 2 entries (e.g. ('saving throw','will') or ('skill','climb') or ('ability','str')
        # reason_for_check is a 'source' type of entry.  See spells.py for explanation of 'source' entries.
        total_mult = 1.
        bonuses = []
        if type(value_being_checked) is not tuple:
            value_being_checked = (value_being_checked,)
        for effect_entry in self.temporary_effects:
            if 'mult' in effect_entry[1]:
                mult_func_list = effect_entry[1]['mult']
                for mult_func in mult_func_list:
                    mult_data = mult_func(effect_entry[0], self, game, value_being_checked = value_being_checked, reason_for_check = reason_for_check)
                    if mult_data:
                        bonuses.append(mult_data)
        for effect_entry in self.permanent_effects:
            if 'mult' in effect_entry[1]:
                mult_func_list = effect_entry[1]['mult']
                for mult_func in mult_func_list:
                    mult_data = mult_func(effect_entry[0], self, game, value_being_checked = value_being_checked, reason_for_check = reason_for_check)
                    if mult_data:
                        bonuses.append(mult_data)
        for effect_entry in self.item_effects:
            if 'mult' in effect_entry[1]:
                mult_func_list = effect_entry[1]['mult']
                for mult_func in mult_func_list:
                    mult_data = mult_func(effect_entry[0], self, game, value_being_checked = value_being_checked, reason_for_check = reason_for_check)
                    if mult_data:
                        bonuses.append(mult_data)
                        
        # compile dict of bonus types, with list of bonus values within each
        bonus_count = {}
        for bonus in bonuses:
            if bonus[0] not in bonus_count:
                bonus_count[bonus[0]] = []
            bonus_count[bonus[0]].append(bonus[1])
            
        for value_list in bonus_count.itervalues():
            this_bonus = -1.
            for value in value_list:
                if value > this_bonus:      # if multiple multiplicative effects of same type (unlikely),
                                            # choose most positive one.
                    this_bonus = value
            total_mult *= this_bonus
            
        return total_mult

#    def find_total_temporary_effect_binary(self, binary_question, game = None, reason_for_check = None):
#        # see conditions.py for list of allowed binary questions
#
#        for effect_entry in self.temporary_effects:
#            if 'binary' in effect_entry[1]:
#                binary_func_list = effect_entry[1]['binary']
#                for binary_func in binary_func_list:
#                    binary_result = binary_func(effect_entry[0], self, game, binary_question = binary_question, reason_for_check = reason_for_check)
#                    if not binary_result:
#                        return False    # all it takes is one False
#        for effect_entry in self.item_effects:
#            if 'binary' in effect_entry[1]:
#                binary_func_list = effect_entry[1]['binary']
#                for binary_func in binary_func_list:
#                    binary_result = binary_func(self, game, binary_question = binary_question, reason_for_check = reason_for_check)
#                    if not binary_result:
#                        return False
#                    
#        return True
    
    def return_all_relevant_effect_bonuses(self, value_being_checked, game = None, reason_for_check = None):
        # value being checked is a tuple.  It might have just one entry (e.g. ('tohit'), or ('str')) or it might have
        # 2 entries (e.g. ('saving throw','will') or ('skill','climb') or ('ability_bonus','str')
        # note that 'ability_bonus' (which affects the bonus, typically changes a die roll) is different 
        # than 'ability' (which affects ability level directly, i.e. +4 to str.
        
        # reason_for_check is a 'source' type of entry.  See spells.py for explanation of 'source' entries.
        bonuses = []
        if type(value_being_checked) is not tuple:
            value_being_checked = (value_being_checked,)
        for effect_entry in self.temporary_effects:
            if 'bonus' in effect_entry[1]:
                bonus_func_list = effect_entry[1]['bonus']
                for bonus_func in bonus_func_list:
                    bonus_data = bonus_func(effect_entry[0], self, game, value_being_checked = value_being_checked, reason_for_check = reason_for_check)
                    if bonus_data:
                        bonuses.append(bonus_data)
        for effect_entry in self.permanent_effects:
            if 'bonus' in effect_entry[1]:
                bonus_func_list = effect_entry[1]['bonus']
                for bonus_func in bonus_func_list:
                    bonus_data = bonus_func(effect_entry[0], self, game, value_being_checked = value_being_checked, reason_for_check = reason_for_check)
                    if bonus_data:
                        bonuses.append(bonus_data)
        for effect_entry in self.item_effects:
            if 'bonus' in effect_entry[1]:
                bonus_func_list = effect_entry[1]['bonus']
                for bonus_func in bonus_func_list:
                    bonus_data = bonus_func(effect_entry[0], self, game, value_being_checked = value_being_checked, reason_for_check = reason_for_check)
                    if bonus_data:
                        bonuses.append(bonus_data)
                
        return bonuses

        
        
        
        
        
#                    if bonus_data:
#                        bonuses.append(bonus_data)
#                        
#        # compile dict of bonus types, with list of bonus values within each
#        bonus_count = {}
#        for bonus in bonuses:
#            if bonus[0] not in bonus_count:
#                bonus_count[bonus[0]] = []
#            bonus_count[bonus[0]].append(bonus[1])
#            
#        for value_list in bonus_count.itervalues():
#            this_bonus = True
#            for value in value_list:
#                if not value:  # can there be both a False and a True response to a binary question
#                                        # for an effect of the same type?  I doubt it.  If so, choose to
#                                        # make a single False dominate.
#                    this_bonus = value
#                    break
#            total_bonus &= this_bonus
#            
#        return total_bonus
#        
#        


    def find_total_effect_binary(self, binary_question, game = None, reason_for_check = None):
        # see conditions.py for list of allowed binary questions

        for effect_entry in self.temporary_effects:
            if 'binary' in effect_entry[1]:
                binary_func_list = effect_entry[1]['binary']
                for binary_func in binary_func_list:
                    binary_result = binary_func(effect_entry[0], self, game, binary_question = binary_question, reason_for_check = reason_for_check)
                    if not binary_result:
                        return False    # all it takes is one False
        for effect_entry in self.permanent_effects:
            if 'binary' in effect_entry[1]:
                binary_func_list = effect_entry[1]['binary']
                for binary_func in binary_func_list:
                    binary_result = binary_func(effect_entry[0], self, game, binary_question = binary_question, reason_for_check = reason_for_check)
                    if not binary_result:
                        return False    # all it takes is one False
        for effect_entry in self.item_effects:
            if 'binary' in effect_entry[1]:
                binary_func_list = effect_entry[1]['binary']
                for binary_func in binary_func_list:
                    binary_result = binary_func(effect_entry[0], self, game, binary_question = binary_question, reason_for_check = reason_for_check)
                    if not binary_result:
                        return False
                    
        return True

            
    def check_triggered_effects(self, trigger, game = None, reason_for_check = None):
        # see conditions.py for list of allowed binary questions

        for effect_entry in self.temporary_effects:
            if 'triggered' in effect_entry[1]:
                triggered_func_list = effect_entry[1]['triggered']
                for triggered_func in triggered_func_list:
                    triggered_func(effect_entry[0], self, game, trigger = trigger, reason_for_check = reason_for_check)
        for effect_entry in self.permanent_effects:
            if 'triggered' in effect_entry[1]:
                triggered_func_list = effect_entry[1]['triggered']
                for triggered_func in triggered_func_list:
                    triggered_func(effect_entry[0], self, game, trigger = trigger, reason_for_check = reason_for_check)
        for effect_entry in self.item_effects:
            if 'triggered' in effect_entry[1]:
                triggered_func_list = effect_entry[1]['triggered']
                for triggered_func in triggered_func_list:
                    triggered_func(effect_entry[0], self, game, trigger = trigger, reason_for_check = reason_for_check)

    def find_total_bonus_old(self, modified_attribute):
        # each self.bonuses entry:
        # modified attribute, bonus type, bonus value, expiration time, source of bonus
        total_bonus = 0
        
        # compile dict of bonus types, with list of bonus values within each
        bonus_count = {}
        for bonus in self.bonuses:
            if bonus[0] == modified_attribute:
                if bonus[1] not in bonus_count:
                    bonus_count[bonus[1]] = []
                bonus_count[bonus[1]].append(bonus[2])
            
        print '************* find total bonus ************', self.bonuses
        for value_list in bonus_count.itervalues():
            this_bonus = -100000
            for value in value_list:
                if value > this_bonus:
                    this_bonus = value
            total_bonus += this_bonus
            
        return total_bonus
        
    def is_invisible(self, game = None, reason_for_check = {}):
        return not self.find_total_effect_binary('not_invisible', game, reason_for_check)
        
    def is_invisible_to_undead(self, game = None, reason_for_check = {}):
        return not self.find_total_effect_binary('detectable_by_undead', game, reason_for_check)

    def is_incorporeal(self, game = None, reason_for_check = {}):
        return not self.find_total_effect_binary('not_incorporeal', game, reason_for_check)
    
    def find_concealment_bonus(self, attacker, game):
        # assumes line of effect exists from source_pos to my pos
        bonuses = []
        if self.pos in attacker.dim_viewed_tiles:
            bonuses.append(['concealment', 20.])
        elif self.pos not in attacker.normal_viewed_tiles:
            bonuses.append(['concealment', 50.])
            
        if self.pos in attacker.normal_viewed_tiles:
            if self.pos in game.map_data[self.map_section]['fog']:
                bonuses.append(['concealment', 20.])

        return bonuses


            
        
        
        
        
        
'armor_class', 'armor bonus', 4, 'Mage Armor'        
                