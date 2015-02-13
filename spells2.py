from copy import deepcopy
try:
    import cPickle as pickle
except:
    import pickle
import random
    

from internalconstants import *
from userconstants import *
from events import *
from gamefunctions import *
import spells
import view_utils
import mobile_object
import hostgamecalcs as hgc
import object_utils
import conditions

class Bane(spells.Spell):
    def __init__(self, **params):
        name = 'bane'
        params.setdefault('display_name', 'Bane')
        params.setdefault('long_desc', "Bane fills your enemies with fear and doubt. Each affected \
        creature takes a -1 penalty on attack rolls and a -1 penalty on \
        saving throws against fear effects. Bane counters and dispels bless")
        params.setdefault('school','enchantment')
        params.setdefault('subschool','compulsion')
        params.setdefault('descriptors', ['fear','mind-affecting'])
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S','DF'])
        spells.Spell.__init__(self,name,**params)
        
        self.radius = 10
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
        caster_items = caster.list_items(True)
        holy_symbol = False
        for item in caster_items:
            if 'holy_symbol' in item.type:
                holy_symbol = True
                break
        if not holy_symbol:
            return False
            
        return True
    
#    def complete_allowed_to_cast(self, caster, target, game):
#        # to determine if target is an allowed target
# 
#        allowed = True
#        if not isinstance( target, mobile_object.MobileObject ):
#            allowed = False
#            
#        max_range = 0.5
#        range_to_targ = self.range_to_target(caster, target) 
#        if max_range < range_to_targ:
#            allowed = False
#            
#        map_section_name = caster.map_section
#        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, radius = int(round(range_to_targ))+1):
#            allowed = False
#            
#        return allowed

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.choose_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
#        idlist = []
#        idlist.extend(game.map_data[map_section_name]['monsters'])
#        idlist.extend(game.charnamesid.itervalues())
#        for id in idlist:
#            obj = game.objectIdDict[id]
#            if self.complete_allowed_to_cast(caster, obj, game):
##                allowed_tiles.add(obj.pos)
#                allowed_targets.add(obj)
        allowed_tiles.add(caster.pos)
        return allowed_tiles, allowed_targets
    
    def area_effect_func(self, map_section_name, mappos, game):
        tile_set = spells.burst_tiles(mappos, map_section_name, game, self.radius)
        return tile_set

    def choose_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose target for ' + self.display_name
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
#        data['target'] = target.id
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        
#        target_id = data['target']
#        target = game.objectIdDict[target_id]
        expiration_time = game.Time + 60 * 1000 * self.find_caster_level(caster) + 1
        effect_details = ['Bane', expiration_time, source]

        origin = caster.pos
        
#        loe_tiles = view_utils.find_loe_tiles_from_position_within_radius(origin, caster.map_section, game, self.radius)
        loe_tiles = self.burst_tiles(origin, map_section_name, game, self.radius)
        if caster.objtype == 'playerchar':
            idlist = game.map_data[map_section_name]['monsters']
        elif caster.objtype == 'monster':
            idlist = game.charnamesid.itervalues()
            
        DC = self.find_spell_DC(caster, source, game)
        for id in idlist:
            enemy = game.objectIdDict[id]
            if enemy.pos in loe_tiles:
                if not hgc.made_saving_throw(enemy.id, 'will', DC, source, game):
                    if hgc.passed_spell_resistance(caster,enemy,self,source,game):            
                        effect_func_str_dict = {}
                        effect_func_str_dict['bonus'] = ['find_bonus']
                        enemy.add_temporary_effect(effect_details, game, effect_func_str_dict, ['Bless'])
                        orddats.append([enemy.id, 'add effect', effect_details, effect_func_str_dict,['Bless']])
                        effects_timed_event_list.append( (caster.subphase+1, expiration_time, [enemy.id, 'effect_expiring', effect_details]) )
        
        return orddats
        
    def find_bonus(self, effect_details, obj, game, value_being_checked = None, reason_for_check = None):
        # source contains information about what is causing the bonus check
        # I'm not sure I can anticipate all the sources.  Try a dict.  See spells.py.
        bonus_data = None
        if value_being_checked[0] == 'tohit':
            bonus_data = ['bane', -1]
            
        if reason_for_check:    
            if 'spell_name' in reason_for_check:
                spell = game.complete_dict_of_spells[reason_for_check['spell_name']]
                if 'fear' in spell.descriptors:
                    if value_being_checked[0] == 'saving_throw':            
                        bonus_data = ['bane',-1] 
        return bonus_data
        
class Bless(spells.Spell):
    def __init__(self, **params):
        name = 'bless'
        params.setdefault('display_name', 'Bless')
        params.setdefault('long_desc', "Bless fills your allies with courage. Each ally gains a +1 morale \
bonus on attack rolls and on saving throws against fear effects.")
        params.setdefault('school','enchantment')
        params.setdefault('subschool','compulsion')
        params.setdefault('descriptors', ['mind-affecting'])
        params.setdefault('classes',{'cleric':1, 'paladin':1})
        params.setdefault('components', ['V','S','DF'])
        spells.Spell.__init__(self,name,**params)
        
        self.radius = 10
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
        caster_items = caster.list_items(True)
        holy_symbol = False
        for item in caster_items:
            if 'holy_symbol' in item.type:
                holy_symbol = True
                break
        if not holy_symbol:
            return False
            
        return True
    
    def selected(self, caster, advclass, game, move_mode = 'phased'):
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.choose_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
#        idlist = []
#        idlist.extend(game.map_data[map_section_name]['monsters'])
#        idlist.extend(game.charnamesid.itervalues())
#        for id in idlist:
#            obj = game.objectIdDict[id]
#            if self.complete_allowed_to_cast(caster, obj, game):
##                allowed_tiles.add(obj.pos)
#                allowed_targets.add(obj)
        allowed_tiles.add(caster.pos)
        return allowed_tiles, allowed_targets
    
    def area_effect_func(self, map_section_name, mappos, game):
        tile_set = spells.burst_tiles(mappos, map_section_name, game, self.radius)
        return tile_set

    def choose_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose target for ' + self.display_name
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
#        data['target'] = target.id
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        
#        target_id = data['target']
#        target = game.objectIdDict[target_id]
        expiration_time = game.Time + 60 * 1000 * self.find_caster_level(caster) + 1
        effect_details = ['Bless', expiration_time, source]

        origin = caster.pos
        
#        loe_tiles = view_utils.find_loe_tiles_from_position_within_radius(origin, caster.map_section, game, self.radius)
        loe_tiles = self.burst_tiles(origin, map_section_name, game, self.radius)
        loe_tiles.add(origin)
        if caster.objtype == 'playerchar':
            idlist = game.charnamesid.itervalues()
        elif caster.objtype == 'monster':
            idlist = game.map_data[map_section_name]['monsters']
            
        for id in idlist:
            friend = game.objectIdDict[id]
            if friend.pos in loe_tiles:
                effect_func_str_dict = {}
                effect_func_str_dict['bonus'] = ['find_bonus']
                friend.add_temporary_effect(effect_details, game, effect_func_str_dict, ['Bane'])
                orddats.append([friend.id, 'add effect', effect_details, effect_func_str_dict,['Bane']])
                effects_timed_event_list.append( (caster.subphase+1, expiration_time, [friend.id, 'effect_expiring', effect_details]) )
        
        return orddats
        
    def find_bonus(self, effect_details, obj, game, value_being_checked = None, reason_for_check = None):
        # source contains information about what is causing the bonus check
        # I'm not sure I can anticipate all the sources.  Try a dict.  See spells.py
        bonus_data = None
        if value_being_checked[0] == 'tohit':
            bonus_data = ['bless', +1]
            
        if reason_for_check:    
            if 'spell_name' in reason_for_check:
                spell = game.complete_dict_of_spells[reason_for_check['spell_name']]
                if 'fear' in spell.descriptors:            
                    if value_being_checked[0] == 'saving_throw':
                        bonus_data = ['bless',+1] 
        return bonus_data
        

class BlessWater(spells.Spell):
    def __init__(self, **params):
        name = 'bless_water'
        params.setdefault('display_name', 'Bless Water')
        params.setdefault('long_desc', "This transmutation imbues a flask (1 pint) of water with positive \
energy, turning it into holy water.  To cast, need to have both 'Five pounds of powdered silver' and a 'Flask of water' \
in inventory.")
        params.setdefault('school','transmutation')
        params.setdefault('descriptors', ['good'])
        params.setdefault('classes',{'cleric':1, 'paladin':1})
        params.setdefault('components', ['V','S','M'])
        params.setdefault('material_components',['five_pounds_powdered_silver','flask_of_water'])
        spells.Spell.__init__(self,name,**params)
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        caster_items = caster.list_items(True)
        silver = False
        water = False
        for idx, item in enumerate(caster_items):
            if item.name == 'five_pounds_powdered_silver':
                silver = True
                self.silver_item = item
            if item.name == 'flask_of_water':
                water = True
                self.water_item = item
        if not silver or not water:
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
            
        return True
    
    def selected(self, caster, advclass, game, move_mode = 'phased'):
        self.as_class = advclass
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.create_order(caster)

    def create_order(self, caster):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = self.as_class
        
        caster.update_actions_used('use_standard_action')
        data = {}
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        
        new_item = object_utils.create_new_item(game.master_object_dict['holy_water'],game)
        game.objectIdDict[new_item.id] = new_item
        pickled_item = pickle.dumps(new_item, pickle.HIGHEST_PROTOCOL)
        orddats.append(['game', 'create new item', pickled_item])
        caster.add_item(new_item, 'storage', None)
        orddats.append([caster_id, 'add item to object', new_item.id, 'storage', None])
        caster.remove_item_no_loc(self.silver_item)
        orddats.append([caster_id, 'remove item from object', self.silver_item.id])
        del game.objectIdDict[self.silver_item.id]
        orddats.append(['game','delete object from id', self.silver_item.id])
        caster.remove_item_no_loc(self.water_item)
        orddats.append([caster_id, 'remove item from object', self.water_item.id])
        del game.objectIdDict[self.water_item.id]
        orddats.append(['game','delete object from id', self.water_item.id])

        return orddats
 
class CauseFear(spells.Spell):
    def __init__(self, **params):
        name = 'cause_fear'
        params.setdefault('display_name', 'Cause Fear')
        params.setdefault('long_desc', "The affected creature becomes frightened. If the subject succeeds on a Will \
        save, it is shaken for 1 round. Creatures with 6 or more HD are immune to this effect.")
        params.setdefault('school','necromancy')
        params.setdefault('descriptors', ['fear','mind-affecting'])
        params.setdefault('classes',{'bard':1, 'cleric':1, 'sorcerer':1, 'wizard': 1})
        params.setdefault('components', ['V','S'])
        spells.Spell.__init__(self,name,**params)
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if game.move_mode != 'phased':
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
            
        return True

    def complete_allowed_to_cast(self, caster, target, game):
        # requires target
#        allowed = self.basic_allowed_to_cast(caster, game)
        if not isinstance( target, mobile_object.MobileObject ):
            return False
        
        if target.num_hit_dice >= 6:
            return False
            
        max_range = 5 + int(self.find_caster_level(caster)/2)
        range_to_targ = self.range_to_target(caster, target) 
        if max_range < range_to_targ:
            return False
            
        map_section_name = caster.map_section
        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, reason = {'obj_id':caster.id}):
            return False
            
        return True
    

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.choose_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section

        allowed_tiles = set()
        allowed_targets = set()
        idlist = []
        idlist.extend(game.map_data[map_section_name]['monsters'])
        idlist.extend(game.charnamesid.itervalues())
        for id in idlist:
            obj = game.objectIdDict[id]
            if self.complete_allowed_to_cast(caster, obj, game):
#                allowed_tiles.add(obj.pos)
                allowed_targets.add(obj)
        return allowed_tiles, allowed_targets
    
    def choose_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose target for ' + self.display_name
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        caster.update_actions_used('use_standard_action')
        data = {}
        data['target'] = target.id
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        target_id = data['target']
        target = game.objectIdDict[target_id]
#        source = {}
#        source['obj_id'] = caster_id
            
        if hgc.passed_spell_resistance(caster,target,self,source,game):            
            DC = self.find_spell_DC(caster, source, game)
            if not hgc.made_saving_throw(target_id, 'will', DC, source, game):
                frightened_roll = random.randint(1,4)                
                expiration_time = game.Time + frightened_roll * (seconds_per_round * 1000) + 1
                source['condition_name'] = 'frightened'
                effect_details = ['Frightened', expiration_time, source]
                effect_func_str_dict = game.dict_of_conditions['frightened'].effect_func_str_dict
                target.add_temporary_effect(effect_details, game, effect_func_str_dict, ['Remove Fear'])
                orddats.append([target_id, 'add effect', effect_details, effect_func_str_dict,['Remove Fear']])
                effects_timed_event_list.append( (caster.subphase+1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
            else:
                expiration_time = game.Time + (seconds_per_round * 1000) + 1
                source['condition_name'] = 'shaken'
                effect_details = ['Shaken', expiration_time, source]
                effect_func_str_dict = game.dict_of_conditions['shaken'].effect_func_str_dict
                target.add_temporary_effect(effect_details, game, effect_func_str_dict, ['Remove Fear'])
                orddats.append([target_id, 'add effect', effect_details, effect_func_str_dict,['Remove Fear']])
                effects_timed_event_list.append( (caster.subphase+1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
        
        return orddats
        
#    def frightened_find_bonus(self, effect_details, obj, game, value_being_checked, reason_for_check = None):
#        return conditions.frightened_find_bonus(effect_details, obj, game, value_being_checked, reason_for_check)
#        
#    def shaken_find_bonus(self, effect_details, obj, game, value_being_checked, reason_for_check = None):
#        return conditions.frightened_find_bonus(effect_details, obj, game, value_being_checked, reason_for_check)
#        
#    def frightened_find_binary(self, effect_details, obj, game, binary_question, reason_for_check = None):
#        return conditions.frightened_find_binary(effect_details, obj, game, binary_question, reason_for_check)

class Command(spells.Spell):
    def __init__(self, **params):
        name = 'command'
        params.setdefault('display_name', 'Command')
        params.setdefault('long_desc', "You give the subject a single command, which it obeys to the best \
of its ability at its earliest opportunity. You may select from the \
following options. \
Approach: On its turn, the subject moves toward you as quickly \
and directly as possible for 1 round. The creature may do nothing \
but move during its turn, and it provokes attacks of opportunity \
for this movement as normal. \
Drop: On its turn, the subject drops whatever it is holding. It \
can't pick up any dropped item until its next turn. \
Fall: On its turn, the subject falls to the ground and remains \
prone for 1 round. It may act normally while prone but takes any \
appropriate penalties. \
Flee: On its turn, the subject moves away from you as quickly as \
possible for 1 round. It may do nothing but move during its turn, and \
it provokes attacks of opportunity for this movement as normal. \
Halt: The subject stands in place for 1 round. It may not take \
any actions but is not considered helpless. \
If the subject can't carry out your command on its next turn, \
the spell automatically fails.")
        params.setdefault('school','enchantment')
        params.setdefault('subschool','compulsion')
        params.setdefault('descriptors', ['language-dependent','mind-affecting'])
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V'])
        spells.Spell.__init__(self,name,**params)
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if game.move_mode != 'phased':
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
            
        return True

    def complete_allowed_to_cast(self, caster, target, game):
        # requires target
#        allowed = self.basic_allowed_to_cast(caster, game)
        if not isinstance( target, mobile_object.MobileObject ):
            return False
        
        if not can_one_mobj_speak_to_another(caster, target, game):
            return False
        
        max_range = 5 + int(self.find_caster_level(caster)/2)
        range_to_targ = self.range_to_target(caster, target) 
        if max_range < range_to_targ:
            return False
            
        map_section_name = caster.map_section
        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, reason = {'obj_id':caster.id}):
            return False
            
        return True
    

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.choose_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section

        allowed_tiles = set()
        allowed_targets = set()
        idlist = []
        idlist.extend(game.map_data[map_section_name]['monsters'])
        idlist.extend(game.charnamesid.itervalues())
        for id in idlist:
            obj = game.objectIdDict[id]
            if self.complete_allowed_to_cast(caster, obj, game):
#                allowed_tiles.add(obj.pos)
                allowed_targets.add(obj)
        return allowed_tiles, allowed_targets
    
    def choose_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose target and then select single command for ' + self.display_name + ' spell.'
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.choose_command, self.cancel_spellcast)
        queue.put(ev)

    def choose_command(self, caster, target, game):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        self.caster = caster
        self.target = target
        data = {}
        data['title'] = 'Choose a command'
        data['choices'] = []
        data['choices'].append('Approach Me')
        data['choices'].append('Drop Items')
        data['choices'].append('Fall Down')
        data['choices'].append('Flee')
        data['choices'].append('Halt')
#        data['choices'] = {}
#        data['choices'][0] = 'Approach Me'
#        data['choices'][1] = 'Drop Items'
#        data['choices'][2] = 'Fall Down'
#        data['choices'][3] = 'Flee'
#        data['choices'][4] = 'Halt'
        ev = ShowDefaultChoicePopup(data,self.create_order)
        queue.put(ev)
                        
    def create_order(self, command_chosen):
        self.caster.update_actions_used('use_standard_action')
        data = {}
        data['target'] = self.target.id
        data['command_chosen'] = command_chosen
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        target_id = data['target']
        target = game.objectIdDict[target_id]
        command_chosen = data['command_chosen']
            
        DC = self.find_spell_DC(caster, source, game)
        if not hgc.made_saving_throw(target_id, 'will', 40, source, game):
            if hgc.passed_spell_resistance(caster,target,self,source,game):            
                expiration_time = game.Time + (seconds_per_round * 1000) + 1
                if command_chosen == 0:
                    new_orders = ['move to target id',caster_id]
                    target.set_new_orders([new_orders], game)
                    hgc.clear_existing_timed_orders_for_id(target_id, game)
                    orddats.append([target_id, 'set new orders', [new_orders]])
                    effect_details = ['Command(Approach)', expiration_time, source]
                    effect_func_str_dict = {}
                    effect_func_str_dict['binary'] = ['approach_find_binary']
                    target.add_temporary_effect(effect_details, game, effect_func_str_dict)
                    orddats.append([target_id, 'add effect', effect_details, effect_func_str_dict])
                    effects_timed_event_list.append( (caster.subphase+1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
                elif command_chosen == 1:
                    hgc.clear_existing_timed_orders_for_id(target_id, game)
                    effect_details = ['Command(Drop Items)', expiration_time, source]
                    effect_func_str_dict = {}
                    effect_func_str_dict['binary'] = ['drop_find_binary']
                    target.add_temporary_effect(effect_details, game, effect_func_str_dict)
                    orddats.append([target_id, 'add effect', effect_details, effect_func_str_dict])
                    effects_timed_event_list.append( (caster.subphase+1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
                    if type(target.items) is dict:
                        for slot in ['mainhand','offhand','bothhands']:
                            if slot in target.items:
                                if target.items[slot]:
                                    # don't create an order for dropping the items.  Don't know how to make sure
                                    # target doesn't delete the order before it takes effect.  Instead, add an event
                                    # to orders events so that target drops items at end of caster's subphase.  This isn't
                                    # truly the beginning of monster's turn, but have to do it this way because also 
                                    # couldn't be sure that target's timed orders wouldn't be cleared before items dropped.
                                    # could create a new subphase, a pre-turn subphase, to pair up with each regular subphase...
                                    item = target.items[slot]
                                    effects_timed_event_list.append( (target.subphase-1, game.Time+1, [target_id, 'forced drop item', item.id]) )
                elif command_chosen == 2:
                    hgc.clear_existing_timed_orders_for_id(target_id, game)
                    effect_details = ['Command(Fall Down)', expiration_time, source]
                    effect_func_str_dict = {}
                    effect_func_str_dict['binary'] = ['fall_find_binary']
                    target.add_temporary_effect(effect_details, game, effect_func_str_dict)
                    orddats.append([target_id, 'add effect', effect_details, effect_func_str_dict])
                    effects_timed_event_list.append( (caster.subphase+1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
                    source2 = {}
                    source2['obj_id'] = caster_id
                    source2['condition_name'] = 'prone'
                    effect_details = ['Prone', expiration_time, source2]
                    effect_func_str_dict = game.dict_of_conditions['prone'].effect_func_str_dict
                    target.add_temporary_effect(effect_details, game, effect_func_str_dict)
                    orddats.append([target_id, 'add effect', effect_details, effect_func_str_dict])
                    effects_timed_event_list.append( (target.subphase-1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
                elif command_chosen == 3:
                    effect_details = ['Command(Flee)', expiration_time, source]
                    effect_func_str_dict = {}
                    effect_func_str_dict['binary'] = ['flee_find_binary']
                    target.add_temporary_effect(effect_details, game, effect_func_str_dict)
                    orddats.append([target_id, 'add effect', effect_details, effect_func_str_dict])
                    effects_timed_event_list.append( (caster.subphase+1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
                elif command_chosen == 4:
                    effect_details = ['Command(Halt)', expiration_time, source]
                    effect_func_str_dict = {}
                    effect_func_str_dict['binary'] = ['halt_find_binary']
                    target.add_temporary_effect(effect_details, game, effect_func_str_dict)
                    orddats.append([target_id, 'add effect', effect_details, effect_func_str_dict])
                    effects_timed_event_list.append( (caster.subphase+1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
                
        return orddats
        
    def approach_find_binary(self, effect_details, obj, game, binary_question, reason_for_check = None):
        # 'can_do_cast_somatics','can_speak','can_cast_spell','can_concentrate_on_spell'
        # 'can_do_move_action','can_do_standard_action','can_do_full_action','can_run','can_charge','can_see'
        # 'can_take_actions','can_hear','not_fleeing','can_take_five_foot_step','can_pick_up_items','not_prone','can_stand_up'
        # 'can_attack'
        if binary_question == 'can_choose_orders':
            return False
        elif binary_question == 'can_do_cast_somatics':
            return False
        elif binary_question == 'can_speak':
            return False
        elif binary_question == 'can_cast_spell':
            return False
        elif binary_question == 'can_concentrate_on_spell':
            return False
        elif binary_question == 'can_charge':
            return False
        elif binary_question == 'can_take_five_foot_step':
            return False
        elif binary_question == 'can_pick_up_items':
            return False
        elif binary_question == 'can_attack':
            return False
        
        return True

    def drop_find_binary(self, effect_details, obj, game, binary_question, reason_for_check = None):
        if binary_question == 'can_pick_up_items':
            return False
        return True

    def fall_find_binary(self, effect_details, obj, game, binary_question, reason_for_check = None):
        if binary_question == 'can_stand_up':
            return False
        return True

#    def prone_find_bonus(self, effect_details, obj, game, value_being_checked = None, reason_for_check = None):
#        return conditions.prone_find_bonus(effect_details, obj, game, value_being_checked, reason_for_check)
#
#    def prone_find_binary(self, effect_details, obj, game, binary_question, reason_for_check = None):
#        return conditions.prone_find_binary(effect_details, obj, game, binary_question, reason_for_check)
#
#    def prone_find_mult(self, effect_details, obj, game, value_being_checked = None, reason_for_check = None):
#        return conditions.prone_find_mult(effect_details, obj, game, value_being_checked, reason_for_check)

    def flee_find_binary(self, effect_details, obj, game, binary_question, reason_for_check = None):
        if binary_question == 'can_choose_orders':
            return False
        elif binary_question == 'not_fleeing':
            return False
        return True

    def halt_find_binary(self, effect_details, obj, game, binary_question, reason_for_check = None):
        if binary_question == 'can_take_actions':
            return False
        elif binary_question == 'can_do_free_actions':
            return False
        elif binary_question == 'can_choose_orders':
            return False
        return True


class ComprehendLanguages(spells.Spell):
    def __init__(self, **params):
        name = 'comprehend_languages'
        params.setdefault('display_name', 'Comprehend Languages')
        params.setdefault('long_desc', "You can understand the spoken words of creatures or read \
otherwise incomprehensible written messages. The ability to read \
does not necessarily impart insight into the material, merely its \
literal meaning. The spell enables you to understand or read an \
unknown language, not speak or write it. \
Written material can be read at the rate of one page (250 \
words) per minute. Magical writing cannot be read, though the \
spell reveals that it is magical. This spell can be foiled by certain \
warding magic (such as the secret page and illusory script spells). \
It does not decipher codes or reveal messages concealed in \
otherwise normal text. \
Comprehend languages can be made permanent with a \
permanency spell.")
        params.setdefault('school','divination')
        params.setdefault('classes',{'bard':1, 'cleric':1, 'sorcerer':1, 'wizard':1})
        params.setdefault('components', ['V','S'])
        spells.Spell.__init__(self,name,**params)
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
            
        return True
    
    def selected(self, caster, advclass, game, move_mode = 'phased'):
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.choose_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
#        idlist = []
#        idlist.extend(game.map_data[map_section_name]['monsters'])
#        idlist.extend(game.charnamesid.itervalues())
#        for id in idlist:
#            obj = game.objectIdDict[id]
#            if self.complete_allowed_to_cast(caster, obj, game):
##                allowed_tiles.add(obj.pos)
#                allowed_targets.add(obj)
        allowed_targets.add(caster)
        return allowed_tiles, allowed_targets
    
    def choose_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose target for ' + self.display_name
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
#        data['target'] = target.id
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        
#        target_id = data['target']
#        target = game.objectIdDict[target_id]
        expiration_time = game.Time + 600 * 1000 * self.find_caster_level(caster) + 1
        effect_details = ['Comprehend Languages', expiration_time, source]

        effect_func_str_dict = {}
        effect_func_str_dict['binary'] = ['find_binary']
        caster.add_temporary_effect(effect_details, game,effect_func_str_dict)
        orddats.append([caster.id, 'add effect', effect_details,effect_func_str_dict])
        effects_timed_event_list.append( (caster.subphase+1, expiration_time, [caster.id, 'effect_expiring', effect_details]) )
        
        return orddats
        
    def find_binary(self, effect_details, obj, game, binary_question, reason_for_check = {}):
        if binary_question == 'cant_understand_all_languages':
            return False
        return True

class CureLightWounds(spells.Spell):
    def __init__(self, **params):
        name = 'cure_light_wounds'
        params.setdefault('display_name', 'Cure Light Wounds')
        params.setdefault('long_desc', "When laying your hand upon a living creature, you channel \
positive energy that cures 1d8 points of damage + 1 point per \
caster level (maximum +5). Since undead are powered by negative \
energy, this spell deals damage to them instead of curing their \
wounds. An undead creature can apply spell resistance, and can \
attempt a Will save to take half damage.")
        params.setdefault('school','conjuration')
        params.setdefault('subschool','healing')
        params.setdefault('classes',{'bard':1,'cleric':1,'druid':1,'paladin':1,'ranger':2})
        spells.Spell.__init__(self,name,**params)
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
            
        return True
    
    def complete_allowed_to_cast(self, caster, target, game):
        if not isinstance( target, mobile_object.MobileObject ):
            return False
            
        max_range = 1.5
        range_to_targ = self.range_to_target(caster, target) 
        if max_range < range_to_targ:
            return False
            
        map_section_name = caster.map_section
        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, reason = {'obj_id':caster.id}):
            return False
        
        if target.type != 'undead' and not target.breathes:
            return False
            
        return True

    def selected(self, caster, advclass, game):
        # function called when this spell is selected
        # to be cast
        
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.choose_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
        caster = game.objectIdDict[source['obj_id']]
        advclass = source['spell_as_class']
        map_section_name = caster.map_section
        allowed_tiles = set()
        allowed_targets = set()
        idlist = []
        idlist.extend(game.map_data[map_section_name]['monsters'])
        idlist.extend(game.charnamesid.itervalues())
        for id in idlist:
            obj = game.objectIdDict[id]
            if self.complete_allowed_to_cast(caster, obj, game):
#                allowed_tiles.add(obj.pos)
                allowed_targets.add(obj)
        return allowed_tiles, allowed_targets

    def choose_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        self.source['attack_type'] = 'melee touch'
        msg = 'Right click to choose target for ' + self.display_name
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
        data['target'] = target.id
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        orddats = []
        
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        caster_level = self.find_caster_level(caster)
        target_id = data['target']
        target = game.objectIdDict[target_id]
        extra = min(5,caster_level)
        orddats = []
        
        if target.type != 'undead':
            heal_roll = random.randint(1,8)
            heal_amt = heal_roll + extra
            target.change_damage(-heal_amt)
            damage_details = {}
            damage_details['enemy_id'] = caster_id
            damage_details['tohit_roll'] = None
            damage_details['tohit_bonus'] = None 
            damage_details['damage_rolls'] = [[heal_roll]]   # each element is a list of die rolls
            damage_details['damage_total'] = [-heal_amt]    # each element is the total damage
            damage_details['damage_type'] = ['positive_energy']
            damage_details['damage_avoided'] = [[0,None]] # each element is a 2 element list [dam_change, change_method]
            
            orddats.append([target_id, 'damage dealt', damage_details])
            
        else:
            if hgc.passed_spell_resistance(caster,target,self,source,game):            
                DC = self.find_spell_DC(caster, source, game)
                if not hgc.made_saving_throw(target_id, 'will', DC, source, game):
                    damage_details_list = [ [1, [1,8], extra, 'positive_energy'] ]
                else:
                    damage_details_list = [ [1, [1,4], int(extra/2.), 'positive_energy'] ]
                base_attack_bonuses = caster.find_base_attack_bonuses(target)
                hgc.execute_melee_touch_attack(caster, target, base_attack_bonuses[0], source, game, damage_details_list)
                    
        return orddats
        

class CurseWater(spells.Spell):
    def __init__(self, **params):
        name = 'curse_water'
        params.setdefault('display_name', 'Curse Water')
        params.setdefault('long_desc', "This spell imbues a flask (1 pint) of water with negative energy, turning it \
        into unholy water. Unholy water damages good outsiders the way holy water damages undead and evil \
        outsiders.  To cast, need to have both 'Five pounds of powdered silver' and a 'Flask of water' \
in inventory.")
        params.setdefault('school','necromancy')
        params.setdefault('descriptors', ['evil'])
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S','M'])
        params.setdefault('material_components',['five_pounds_powdered_silver','flask_of_water'])
        spells.Spell.__init__(self,name,**params)
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        caster_items = caster.list_items(True)
        silver = False
        water = False
        for idx, item in enumerate(caster_items):
            if item.name == 'five_pounds_powdered_silver':
                silver = True
                self.silver_item = item
            if item.name == 'flask_of_water':
                water = True
                self.water_item = item
        if not silver or not water:
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
            
        return True
    
    def selected(self, caster, advclass, game, move_mode = 'phased'):
        self.as_class = advclass
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.create_order(caster,game)

    def create_order(self, caster,game):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = self.as_class
        
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        
        new_item = object_utils.create_new_item(game.master_object_dict['unholy_water'],game)
        game.objectIdDict[new_item.id] = new_item
        pickled_item = pickle.dumps(new_item, pickle.HIGHEST_PROTOCOL)
        orddats.append(['game', 'create new item', pickled_item])
        caster.add_item(new_item, 'storage', None)
        orddats.append([caster_id, 'add item to object', new_item.id, 'storage', None])
        caster.remove_item_no_loc(self.silver_item)
        orddats.append([caster_id, 'remove item from object', self.silver_item.id])
        del game.objectIdDict[self.silver_item.id]
        orddats.append(['game','delete object from id', self.silver_item.id])
        caster.remove_item_no_loc(self.water_item)
        orddats.append([caster_id, 'remove item from object', self.water_item.id])
        del game.objectIdDict[self.water_item.id]
        orddats.append(['game','delete object from id', self.water_item.id])

        return orddats
 

class Deathwatch(spells.Spell):
    def __init__(self, **params):
        name = 'deathwatch'
        params.setdefault('display_name', 'Deathwatch')
        params.setdefault('long_desc', "Using the powers of necromancy, you can determine the \
        condition of creatures near death within the spell's range. You instantly know whether \
        each creature within the area is dead, fragile (alive and wounded, with 3 or fewer hit \
        points left), fighting off death (alive with 4 or more hit points but less than 2/3 of max), healthy, undead, or \
        neither alive nor dead (such as a construct). Deathwatch sees through any spell or ability \
        that allows creatures to feign death.  If cast during phased mode, you will get to choose \
        a new cone of detection before your turn each round.  If cast during free move mode, you will \
        get to choose a new cone of detection every 15 sec or when you have no other orders pending, \
        whichever occurs later.")
        params.setdefault('school','necromancy')
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S'])
        spells.Spell.__init__(self,name,**params)
        
        self.radius = 6
        self.caster_pos = None
        self.reset_time = 15    # time in seconds after caster chooses cone that the game
                                # asks for next cone. 
        
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
            
        return True
    
#    def complete_allowed_to_cast(self, caster, target, game):
#        # to determine if target is an allowed target
# 
#        allowed = True
#        if not isinstance( target, mobile_object.MobileObject ):
#            allowed = False
#            
#        max_range = 0.5
#        range_to_targ = self.range_to_target(caster, target) 
#        if max_range < range_to_targ:
#            allowed = False
#            
#        map_section_name = caster.map_section
#        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, radius = int(round(range_to_targ))+1):
#            allowed = False
#            
#        return allowed

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        self.caster_pos = caster.pos
        self.choose_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
        pos = caster.lastOrderedPos
        self.caster_pos = pos
        adj = findAdjTiles(pos[0],pos[1], game.map[caster.map_section])
        for tile in adj:
            allowed_tiles.add(tile)
        return allowed_tiles, allowed_targets
    
    def area_effect_func(self, map_section_name, mappos, game):
        self.tile_set = spells.cone_tiles(mappos, map_section_name, game, self.radius,self.caster_pos)
        return self.tile_set

    def choose_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose cone area for ' + self.display_name
        
        print '################# spells2, deathwatch, choose_target #####################'
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
#        ev = UnblockFreeMoveResultsOnClientEvent()
#        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        tile_set = data['tile set']
        
        idlist = []
        if caster.objtype == 'playerchar':
            idlist.extend(game.map_data[map_section_name]['monsters'])
        idlist.extend(game.charnamesid.itervalues())
        life_msg = 'Deathwatch spell result:'
        obj_found = False
        for oid in idlist:
            obj = game.objectIdDict[oid]
            if obj.pos in tile_set:
                obj_found = True
                if life_msg:
                    life_msg += '\n'
                life_msg += self.find_hp_msg(obj)
        if not obj_found:
            life_msg += '\n' + 'Nothing detected'
                
        print '################ spells2, effect ********* ################'
        orddats.append(['game', 'show message', life_msg])
        expiration_time = game.Time + 600 * 1000 * self.find_caster_level(caster) + 1
        other_data_client = [source, 'choose_target_2', [expiration_time]]
#        other_data_host = [source, 'schedule_next',expiration_time]
        
#        Structure of an event entry in timed_event_lists:
#        (subphase, execution time, event details)
#        
#        Structure of event details:
#        [object_id, event type, anything else]
        
        if game.move_mode == 'phased':
            print '################ spells2, effect ################'
            orddats.append([caster.id, 'call function before orders', other_data_client])
        else:
            reset_time = game.Time + self.reset_time * 1000
            effects_timed_event_list.append( (caster.subphase-1, reset_time, [None, 'create orddat entry', [caster.id, 'call function before orders', other_data_client]]) )
#            effects_timed_event_list.append( (caster.subphase-1, reset_time, [caster.id, 'client call function', other_data_client]) )
            
        return orddats
        
        
                
        # todo - add choice of cone location at start of each round
        # todo - make timer for this choice in free move mode
        
    def find_hp_msg(self,obj):
        # hostcomplete
        curr_hp = obj.find_current_hit_points()
        msg = ''
        if  curr_hp < 0:
            msg = obj.display_name + ' is dead'
        elif curr_hp <= 3:
            msg = obj.display_name + ' is fragile'
        elif curr_hp < 2*obj.find_current_max_hp()/3:
            msg = obj.display_name + ' is fighting off death'
        else:
            msg = obj.display_name + ' is healthy'
#        elif curr_hp == obj.find_current_max_hp():
#            msg = obj.display_name + ' is healthy'
            
        if obj.type == 'undead':
            if curr_hp < 0:
                msg += ' and was undead'
            else:
                msg += ' and is undead'
        elif not obj.breathes:
            if curr_hp < 0:
                msg += ' and was neither alive nor dead'
            else:
                msg += ' and is neither alive nor dead'
        if msg:
            msg += '.'
        return msg

    def choose_target_2(self, source, extra_data):
        # client, from 'client call function' event on hostcomplete via clientroundresults.py
        # extra_data is the 3rd argument in 'other_data_client' in the above 'effect' method.
        self.source = source
        self.extra_data = extra_data
#        self.other_data = deepcopy(other_data)
        msg = "Right click to choose new cone for " + self.display_name + " (it's a free action) \
or Cancel the spell."
        print '################# spells2, deathwatch, choose_target2 #####################'
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order_2, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)

    def create_order_2(self, caster, target, game):
        # on client, after target has been chosen
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['extra'] = deepcopy(self.extra_data[0])
        source = deepcopy(self.source)
        data['source'] = source
        self.source = {}
        self.extra_data = []
        
        print '############### spells 2, deathwatch, create order 2 #############'
#        ev = UnblockFreeMoveResultsOnClientEvent()
#        queue.put(ev)
        ev = SendDataFromClientToHostEvent('host call function', [source, 'effect_2', data], game.myprofname, False)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect_2(self, data, game):
        # on hostcomplete
        print '############### spells 2, deathwatch, effect 2 #############'
#        orddats = []
        source = data['source']
        tile_set = data['tile set']
        expiration_time = data['extra']
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        
        idlist = []
        if caster.objtype == 'playerchar':
            idlist.extend(game.map_data[map_section_name]['monsters'])
        idlist.extend(game.charnamesid.itervalues())
        life_msg = 'Deathwatch spell result\:'
        obj_found = False
        for oid in idlist:
            obj = game.objectIdDict[oid]
            print '############# spells 2, effect 2 ############', obj.display_name
            if obj.pos in tile_set:
                print '############# spells 2, effect 2 tile set ############', obj.display_name, tile_set
                obj_found = True
                if life_msg:
                    life_msg += '\n'
                life_msg += self.find_hp_msg(obj)
        if not obj_found:
            life_msg += '\n' + 'Nothing detected'
                
        #orddats.append(['game', 'show message', life_msg])
        ev = HostSendDataEvent('show_timed_message',[life_msg,True])
        queue.put(ev)

        other_data_client = [source, 'choose_target_2', [expiration_time]]
        if game.move_mode == 'phased':
            print '################ spells2, effect ################'
            effects_timed_event_list.append( (caster.subphase-1, 0, [None, 'create orddat entry', [caster.id, 'call function before orders', other_data_client]]) )
#            orddats.append([caster.id, 'call function before turn', other_data_client])
        else:
            reset_time = game.Time + self.reset_time * 1000
            effects_timed_event_list.append( (caster.subphase-1, reset_time, [None, 'create orddat entry', [caster.id, 'call function before orders', other_data_client]]) )
#            effects_timed_event_list.append( (caster.subphase-1, reset_time, [caster.id, 'client call function', other_data_client]) )


aura_dict = {}
aura_dict['Overwhelming'] = 4
aura_dict['Strong'] = 3
aura_dict['Moderate'] = 2
aura_dict['Faint'] = 1
#aura_dict['None'] = 0
        
class DetectChaos(spells.Spell):
    def __init__(self, **params):
        name = 'detect_chaos'
        params.setdefault('display_name', 'Detect Chaos')
        params.setdefault('long_desc', "You can sense the presence of chaos. The amount of information revealed depends on \
how long you study a particular area or subject. \n\
    1st Round: Presence or absence of chaos. \n\
    2nd Round: Number of chaotic auras (creatures, objects, or spells) in the area and the power of the most potent chaotic aura present. \
               If you are of lawful alignment, and the strongest chaotic aura's power is overwhelming (see below), and the HD or level of \
               the aura's source is at least twice your character level, you are stunned for 1 round and the spell ends. \n\
    3rd Round: The power and location of each aura. If an aura is outside your line of sight, then you discern its direction but \
               not its exact location. \n\
Aura Power: A chaotic aura's power depends on the type of chaotic creature or object that you're detecting and its HD, caster level, or \
(in the case of a cleric) class level; see the table below. If an aura falls into more than one strength category, the spell indicates \
the stronger of the two. \n\
If cast during phased mode each round you will get to choose whether to concentrate on the same area (thereby allowing progression to 2nd \
or 3rd round), or choose a new cone of detection. Either requires a standard action. \n\
If cast during free move mode, you will get to choose a cone of detection every 15 sec or when \
you have no other orders pending, whichever occurs later.  If more than 30 sec have passed since previous detection, then it is decreed \
that you didn't concentrate on the spell and it ends.  If you are at the same location when the choice appears and less than 30 sec \
have passed since previous detection, then you will get the option of continuing to concentrate on the same area (thereby allowing \
progression to 2nd or 3rd round).")
        params.setdefault('school','divination')
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S','DF'])
        spells.Spell.__init__(self,name,**params)
        
        self.radius = 12
        self.caster_pos = None
        self.reset_time = 15    # time in seconds after caster chooses cone that the game
                                # asks for next cone. 
        
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
        caster_items = caster.list_items(True)
        holy_symbol = False
        for item in caster_items:
            if 'holy_symbol' in item.type:
                holy_symbol = True
                break
        if not holy_symbol:
            return False
            
        return True
    
#    def complete_allowed_to_cast(self, caster, target, game):
#        # to determine if target is an allowed target
# 
#        allowed = True
#        if not isinstance( target, mobile_object.MobileObject ):
#            allowed = False
#            
#        max_range = 0.5
#        range_to_targ = self.range_to_target(caster, target) 
#        if max_range < range_to_targ:
#            allowed = False
#            
#        map_section_name = caster.map_section
#        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, radius = int(round(range_to_targ))+1):
#            allowed = False
#            
#        return allowed

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        self.caster_pos = caster.pos
        self.choose_first_round_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
        pos = caster.lastOrderedPos
        self.caster_pos = pos
        adj = findAdjTiles(pos[0],pos[1], game.map[caster.map_section])
        for tile in adj:
            allowed_tiles.add(tile)
        return allowed_tiles, allowed_targets
    
    def area_effect_func(self, map_section_name, mappos, game):
        self.tile_set = spells.cone_tiles(mappos, map_section_name, game, self.radius,self.caster_pos)
        return self.tile_set

    def choose_first_round_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
        
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
#        ev = UnblockFreeMoveResultsOnClientEvent()
#        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        if hasattr(self,'caster'):
            self.caster.concentration_data = None

    def effect(self, source, data, game):
        # only executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        tile_set = data['tile set']
        
        if 'expiration time' in data:
            expiration_time = data['expiration time']
        else:
            expiration_time = game.Time + 600 * 1000 * self.find_caster_level(caster) + 1
        extra = [expiration_time, caster.pos, data, game.Time]
            
        aura_list = self.find_auras(game, tile_set)   
            
        if data['round'] == 1:
            detect_msg = 'Detect Chaos spell, round 1 result:'
            if aura_list:
                detect_msg += '\n' + 'Chaos present'
            else:
                detect_msg += '\n' + 'No chaos detected'
            other_data_client = [source, 'choose_round_2_action', extra]
        elif data['round'] == 2:
            detect_msg = 'Detect Chaos spell, round 2 result:'
            num_found = len(aura_list)
            strongest_aura = None
            strongest_aura_number = 0
            for aura in aura_list:
                if aura_dict[aura[1]] > strongest_aura_number:
                    strongest_aura = aura[1]
            if num_found == 0:
                detect_msg += '\n' + 'No chaos detected'
            else:
                detect_msg += '\n' + str(num_found) + ' chaotic things found.\n'
                detect_msg += 'Most powerful aura is ' + strongest_aura + '.'
            other_data_client = [source, 'choose_round_3_action', extra]
            
        elif data['round'] == 3:
            detect_msg = 'Detect Chaos spell, round 3 result:'
            if not aura_list:
                detect_msg += '\n' + 'No chaos detected'
            else:
                for aura in aura_list:
                    pos = aura[0]
                    pos_str = ' North ' + str(caster.pos[1] - pos[1]) + ' squares and East ' + str(pos[0] - caster.pos[0]) + ' squares.' 
                    detect_msg += '\n' + aura[1] + ' aura.' + pos_str
            other_data_client = [source, 'choose_round_1_action', extra]
        orddats.append(['game', 'show message', detect_msg])
        
#        Structure of an event entry in timed_event_lists:
#        (subphase, execution time, event details)
#        
#        Structure of event details:
#        [object_id, event type, anything else]
        
        if game.move_mode == 'phased':
            orddats.append([caster.id, 'add spell concentration data', other_data_client])
        else:
            reset_time = game.Time + self.reset_time * 1000
            effects_timed_event_list.append( (caster.subphase-1, reset_time, [None, 'create orddat entry', [caster.id, 'call function before orders', other_data_client]]) )
#            effects_timed_event_list.append( (caster.subphase-1, reset_time, [caster.id, 'client call function', other_data_client]) )
            
        return orddats

    def find_auras(self, game, tile_set):
        aura_list = []
        objlist = game.objectIdDict.itervalues()
        for obj in objlist:
            if not hasattr(obj, 'carried') \
            or (hasattr(obj, 'carried') and not obj.carried):
                if obj.pos in tile_set:
                    if 'chaotic' in obj.alignment:
                        aura = find_aura_power(obj)
                        if aura:
                            aura_list.append((obj.pos,aura))
                    for effect_entry in obj.temporary_effects:
                        effect = effect_entry[0]
                        e_source = effect[2]
                        if 'spell_name' in e_source:
                            spell = game.complete_dict_of_spells[e_source['spell_name']]
                            if 'chaotic' in spell.descriptors:
                                aura = find_spell_aura_power(spell, e_source, game)
                                if aura:
                                    aura_list.append((obj.pos,aura))
                    obj_items = obj.list_items(True)
                    for item in obj_items:
                        if 'chaotic' in item.alignment:
                            aura = find_aura_power(item)
                            if aura:
                                aura_list.append((obj.pos,aura))
                        for effect_entry in item.temporary_effects:
                            effect = effect_entry[0]
                            e_source = effect[2]
                            if 'spell_name' in e_source:
                                spell = game.complete_dict_of_spells[e_source['spell_name']]
                                if 'chaotic' in spell.descriptors:
                                    aura = find_spell_aura_power(spell, e_source, game)
                                    if aura:
                                        aura_list.append((obj.pos,aura))
        return aura_list
        
    def choose_round_2_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 2nd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_2_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_2_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_2_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_2_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 2
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_3_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 3rd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_3_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_3_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_3_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_3_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 3
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_1_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
            msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
            ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_round_1_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
            queue.put(ev)

    def create_round_1_order(self, caster, target, game):
#        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
        
class DetectLaw(spells.Spell):
    def __init__(self, **params):
        name = 'detect_law'
        params.setdefault('display_name', 'Detect Law')
        params.setdefault('long_desc', "You can sense the presence of lawful objects and spells. The amount of information revealed depends on \
how long you study a particular area or subject. \n\
    1st Round: Presence or absence of law. \n\
    2nd Round: Number of lawful auras (creatures, objects, or spells) in the area and the power of the most potent lawful aura present. \
               If you are of chaotic alignment, and the strongest lawful aura's power is overwhelming (see below), and the HD or level of \
               the aura's source is at least twice your character level, you are stunned for 1 round and the spell ends. \n\
    3rd Round: The power and location of each aura. If an aura is outside your line of sight, then you discern its direction but \
               not its exact location. \n\
Aura Power: A lawful aura's power depends on the type of lawful creature or object that you're detecting and its HD, caster level, or \
(in the case of a cleric) class level; see the table below. If an aura falls into more than one strength category, the spell indicates \
the stronger of the two. \n\
If cast during phased mode each round you will get to choose whether to concentrate on the same area (thereby allowing progression to 2nd \
or 3rd round), or choose a new cone of detection. Either requires a standard action. \n\
If cast during free move mode, you will get to choose a cone of detection every 15 sec or when \
you have no other orders pending, whichever occurs later.  If more than 30 sec have passed since previous detection, then it is decreed \
that you didn't concentrate on the spell and it ends.  If you are at the same location when the choice appears and less than 30 sec \
have passed since previous detection, then you will get the option of continuing to concentrate on the same area (thereby allowing \
progression to 2nd or 3rd round).")
        params.setdefault('school','divination')
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S','DF'])
        spells.Spell.__init__(self,name,**params)
        
        self.radius = 12
        self.caster_pos = None
        self.reset_time = 15    # time in seconds after caster chooses cone that the game
                                # asks for next cone. 
        
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
        caster_items = caster.list_items(True)
        holy_symbol = False
        for item in caster_items:
            if 'holy_symbol' in item.type:
                holy_symbol = True
                break
        if not holy_symbol:
            return False
            
        return True
    
#    def complete_allowed_to_cast(self, caster, target, game):
#        # to determine if target is an allowed target
# 
#        allowed = True
#        if not isinstance( target, mobile_object.MobileObject ):
#            allowed = False
#            
#        max_range = 0.5
#        range_to_targ = self.range_to_target(caster, target) 
#        if max_range < range_to_targ:
#            allowed = False
#            
#        map_section_name = caster.map_section
#        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, radius = int(round(range_to_targ))+1):
#            allowed = False
#            
#        return allowed

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        self.caster_pos = caster.pos
        self.choose_first_round_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
        pos = caster.lastOrderedPos
        self.caster_pos = pos
        adj = findAdjTiles(pos[0],pos[1], game.map[caster.map_section])
        for tile in adj:
            allowed_tiles.add(tile)
        return allowed_tiles, allowed_targets
    
    def area_effect_func(self, map_section_name, mappos, game):
        self.tile_set = spells.cone_tiles(mappos, map_section_name, game, self.radius,self.caster_pos)
        return self.tile_set

    def choose_first_round_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
        
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
#        ev = UnblockFreeMoveResultsOnClientEvent()
#        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        if hasattr(self,'caster'):
            self.caster.concentration_data = None

    def effect(self, source, data, game):
        # only executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        tile_set = data['tile set']
        
        if 'expiration time' in data:
            expiration_time = data['expiration time']
        else:
            expiration_time = game.Time + 600 * 1000 * self.find_caster_level(caster) + 1
        extra = [expiration_time, caster.pos, data, game.Time]
            
        aura_list = self.find_auras(game, tile_set)   
            
        if data['round'] == 1:
            detect_msg = 'Detect Law spell, round 1 result:'
            if aura_list:
                detect_msg += '\n' + 'Law present'
            else:
                detect_msg += '\n' + 'No law detected'
            other_data_client = [source, 'choose_round_2_action', extra]
        elif data['round'] == 2:
            detect_msg = 'Detect Law spell, round 2 result:'
            num_found = len(aura_list)
            strongest_aura = None
            strongest_aura_number = 0
            for aura in aura_list:
                if aura_dict[aura[1]] > strongest_aura_number:
                    strongest_aura = aura[1]
            if num_found == 0:
                detect_msg += '\n' + 'No law detected'
            else:
                detect_msg += '\n' + str(num_found) + ' lawful things found.\n'
                detect_msg += 'Most powerful aura is ' + strongest_aura + '.'
            other_data_client = [source, 'choose_round_3_action', extra]
            
        elif data['round'] == 3:
            detect_msg = 'Detect Law spell, round 3 result:'
            if not aura_list:
                detect_msg += '\n' + 'No law detected'
            else:
                for aura in aura_list:
                    pos = aura[0]
                    pos_str = ' North ' + str(caster.pos[1] - pos[1]) + ' squares and East ' + str(pos[0] - caster.pos[0]) + ' squares.' 
                    detect_msg += '\n' + aura[1] + ' aura.' + pos_str
            other_data_client = [source, 'choose_round_1_action', extra]
        orddats.append(['game', 'show message', detect_msg])
        
#        Structure of an event entry in timed_event_lists:
#        (subphase, execution time, event details)
#        
#        Structure of event details:
#        [object_id, event type, anything else]
        
        if game.move_mode == 'phased':
            orddats.append([caster.id, 'add spell concentration data', other_data_client])
        else:
            reset_time = game.Time + self.reset_time * 1000
            effects_timed_event_list.append( (caster.subphase-1, reset_time, [None, 'create orddat entry', [caster.id, 'call function before orders', other_data_client]]) )
#            effects_timed_event_list.append( (caster.subphase-1, reset_time, [caster.id, 'client call function', other_data_client]) )
            
        return orddats

    def find_auras(self, game, tile_set):
        aura_list = []
        objlist = game.objectIdDict.itervalues()
        for obj in objlist:
            if not hasattr(obj, 'carried') \
            or (hasattr(obj, 'carried') and not obj.carried):
                if obj.pos in tile_set:
                    if 'lawful' in obj.alignment:
                        aura = find_aura_power(obj)
                        if aura:
                            aura_list.append((obj.pos,aura))
                    for effect_entry in obj.temporary_effects:
                        effect = effect_entry[0]
                        e_source = effect[2]
                        if 'spell_name' in e_source:
                            spell = game.complete_dict_of_spells[e_source['spell_name']]
                            if 'lawful' in spell.descriptors:
                                aura = find_spell_aura_power(spell, e_source, game)
                                if aura:
                                    aura_list.append((obj.pos,aura))
                    obj_items = obj.list_items(True)
                    for item in obj_items:
                        if 'lawful' in item.alignment:
                            aura = find_aura_power(item)
                            if aura:
                                aura_list.append((obj.pos,aura))
                        for effect_entry in item.temporary_effects:
                            effect = effect_entry[0]
                            e_source = effect[2]
                            if 'spell_name' in e_source:
                                spell = game.complete_dict_of_spells[e_source['spell_name']]
                                if 'lawful' in spell.descriptors:
                                    aura = find_spell_aura_power(spell, e_source, game)
                                    if aura:
                                        aura_list.append((obj.pos,aura))
        return aura_list
        
    def choose_round_2_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 2nd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_2_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_2_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_2_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_2_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 2
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_3_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 3rd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_3_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_3_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_3_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_3_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 3
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_1_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
            msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
            ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_round_1_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
            queue.put(ev)

    def create_round_1_order(self, caster, target, game):
#        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
        
class DetectEvil(spells.Spell):
    def __init__(self, **params):
        name = 'detect_evil'
        params.setdefault('display_name', 'Detect Evil')
        params.setdefault('long_desc', "You can sense the presence of evil objects and spells. The amount of information revealed depends on \
how long you study a particular area or subject. \n\
    1st Round: Presence or absence of evil. \n\
    2nd Round: Number of evil auras (creatures, objects, or spells) in the area and the power of the most potent evil aura present. \
               If you are of good alignment, and the strongest evil aura's power is overwhelming (see below), and the HD or level of \
               the aura's source is at least twice your character level, you are stunned for 1 round and the spell ends. \n\
    3rd Round: The power and location of each aura. If an aura is outside your line of sight, then you discern its direction but \
               not its exact location. \n\
Aura Power: An evil aura's power depends on the type of evil creature or object that you're detecting and its HD, caster level, or \
(in the case of a cleric) class level; see the table below. If an aura falls into more than one strength category, the spell indicates \
the stronger of the two. \n\
If cast during phased mode each round you will get to choose whether to concentrate on the same area (thereby allowing progression to 2nd \
or 3rd round), or choose a new cone of detection. Either requires a standard action. \n\
If cast during free move mode, you will get to choose a cone of detection every 15 sec or when \
you have no other orders pending, whichever occurs later.  If more than 30 sec have passed since previous detection, then it is decreed \
that you didn't concentrate on the spell and it ends.  If you are at the same location when the choice appears and less than 30 sec \
have passed since previous detection, then you will get the option of continuing to concentrate on the same area (thereby allowing \
progression to 2nd or 3rd round).")
        params.setdefault('school','divination')
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S','DF'])
        spells.Spell.__init__(self,name,**params)
        
        self.radius = 12
        self.caster_pos = None
        self.reset_time = 15    # time in seconds after caster chooses cone that the game
                                # asks for next cone. 
        
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
        caster_items = caster.list_items(True)
        holy_symbol = False
        for item in caster_items:
            if 'holy_symbol' in item.type:
                holy_symbol = True
                break
        if not holy_symbol:
            return False
            
        return True
    
#    def complete_allowed_to_cast(self, caster, target, game):
#        # to determine if target is an allowed target
# 
#        allowed = True
#        if not isinstance( target, mobile_object.MobileObject ):
#            allowed = False
#            
#        max_range = 0.5
#        range_to_targ = self.range_to_target(caster, target) 
#        if max_range < range_to_targ:
#            allowed = False
#            
#        map_section_name = caster.map_section
#        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, radius = int(round(range_to_targ))+1):
#            allowed = False
#            
#        return allowed

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        self.caster_pos = caster.pos
        self.choose_first_round_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
        pos = caster.lastOrderedPos
        self.caster_pos = pos
        adj = findAdjTiles(pos[0],pos[1], game.map[caster.map_section])
        for tile in adj:
            allowed_tiles.add(tile)
        return allowed_tiles, allowed_targets
    
    def area_effect_func(self, map_section_name, mappos, game):
        self.tile_set = spells.cone_tiles(mappos, map_section_name, game, self.radius,self.caster_pos)
        return self.tile_set

    def choose_first_round_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
        
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
#        ev = UnblockFreeMoveResultsOnClientEvent()
#        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        if hasattr(self,'caster'):
            self.caster.concentration_data = None

    def effect(self, source, data, game):
        # only executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        tile_set = data['tile set']
        
        if 'expiration time' in data:
            expiration_time = data['expiration time']
        else:
            expiration_time = game.Time + 600 * 1000 * self.find_caster_level(caster) + 1
        extra = [expiration_time, caster.pos, data, game.Time]
            
        aura_list = self.find_auras(game, tile_set)   
            
        if data['round'] == 1:
            detect_msg = 'Detect Evil spell, round 1 result:'
            if aura_list:
                detect_msg += '\n' + 'Evil present'
            else:
                detect_msg += '\n' + 'No evil detected'
            other_data_client = [source, 'choose_round_2_action', extra]
        elif data['round'] == 2:
            detect_msg = 'Detect Evil spell, round 2 result:'
            num_found = len(aura_list)
            strongest_aura = None
            strongest_aura_number = 0
            for aura in aura_list:
                if aura_dict[aura[1]] > strongest_aura_number:
                    strongest_aura = aura[1]
            if num_found == 0:
                detect_msg += '\n' + 'No evil detected'
            else:
                detect_msg += '\n' + str(num_found) + ' evil things found.\n'
                detect_msg += 'Most powerful aura is ' + strongest_aura + '.'
            other_data_client = [source, 'choose_round_3_action', extra]
            
        elif data['round'] == 3:
            detect_msg = 'Detect Evil spell, round 3 result:'
            if not aura_list:
                detect_msg += '\n' + 'No evil detected'
            else:
                for aura in aura_list:
                    pos = aura[0]
                    pos_str = ' North ' + str(caster.pos[1] - pos[1]) + ' squares and East ' + str(pos[0] - caster.pos[0]) + ' squares.' 
                    detect_msg += '\n' + aura[1] + ' aura.' + pos_str
            other_data_client = [source, 'choose_round_1_action', extra]
        orddats.append(['game', 'show message', detect_msg])
        
#        Structure of an event entry in timed_event_lists:
#        (subphase, execution time, event details)
#        
#        Structure of event details:
#        [object_id, event type, anything else]
        
        if game.move_mode == 'phased':
            orddats.append([caster.id, 'add spell concentration data', other_data_client])
        else:
            reset_time = game.Time + self.reset_time * 1000
            effects_timed_event_list.append( (caster.subphase-1, reset_time, [None, 'create orddat entry', [caster.id, 'call function before orders', other_data_client]]) )
#            effects_timed_event_list.append( (caster.subphase-1, reset_time, [caster.id, 'client call function', other_data_client]) )
            
        return orddats

    def find_auras(self, game, tile_set):
        aura_list = []
        objlist = game.objectIdDict.itervalues()
        for obj in objlist:
            if not hasattr(obj, 'carried') \
            or (hasattr(obj, 'carried') and not obj.carried):
                if obj.pos in tile_set:
                    if 'evil' in obj.alignment:
                        aura = find_aura_power(obj)
                        if aura:
                            aura_list.append((obj.pos,aura))
                    for effect_entry in obj.temporary_effects:
                        effect = effect_entry[0]
                        e_source = effect[2]
                        if 'spell_name' in e_source:
                            spell = game.complete_dict_of_spells[e_source['spell_name']]
                            if 'evil' in spell.descriptors:
                                aura = find_spell_aura_power(spell, e_source, game)
                                if aura:
                                    aura_list.append((obj.pos,aura))
                    obj_items = obj.list_items(True)
                    for item in obj_items:
                        if 'evil' in item.alignment:
                            aura = find_aura_power(item)
                            if aura:
                                aura_list.append((obj.pos,aura))
                        for effect_entry in item.temporary_effects:
                            effect = effect_entry[0]
                            e_source = effect[2]
                            if 'spell_name' in e_source:
                                spell = game.complete_dict_of_spells[e_source['spell_name']]
                                if 'evil' in spell.descriptors:
                                    aura = find_spell_aura_power(spell, e_source, game)
                                    if aura:
                                        aura_list.append((obj.pos,aura))
        return aura_list
        
    def choose_round_2_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 2nd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_2_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_2_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_2_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_2_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 2
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_3_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 3rd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_3_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_3_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_3_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_3_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 3
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_1_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
            msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
            ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_round_1_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
            queue.put(ev)

    def create_round_1_order(self, caster, target, game):
#        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
class DetectGood(spells.Spell):
    def __init__(self, **params):
        name = 'detect_good'
        params.setdefault('display_name', 'Detect Good')
        params.setdefault('long_desc', "You can sense the presence of good objects and spells. The amount of information revealed depends on \
how long you study a particular area or subject. \n\
    1st Round: Presence or absence of good. \n\
    2nd Round: Number of good auras (creatures, objects, or spells) in the area and the power of the most potent good aura present. \
               If you are of evil alignment, and the strongest good aura's power is overwhelming (see below), and the HD or level of \
               the aura's source is at least twice your character level, you are stunned for 1 round and the spell ends. \n\
    3rd Round: The power and location of each aura. If an aura is outside your line of sight, then you discern its direction but \
               not its exact location. \n\
Aura Power: A good aura's power depends on the type of good creature or object that you're detecting and its HD, caster level, or \
(in the case of a cleric) class level; see the table below. If an aura falls into more than one strength category, the spell indicates \
the stronger of the two. \n\
If cast during phased mode each round you will get to choose whether to concentrate on the same area (thereby allowing progression to 2nd \
or 3rd round), or choose a new cone of detection. Either requires a standard action. \n\
If cast during free move mode, you will get to choose a cone of detection every 15 sec or when \
you have no other orders pending, whichever occurs later.  If more than 30 sec have passed since previous detection, then it is decreed \
that you didn't concentrate on the spell and it ends.  If you are at the same location when the choice appears and less than 30 sec \
have passed since previous detection, then you will get the option of continuing to concentrate on the same area (thereby allowing \
progression to 2nd or 3rd round).")
        params.setdefault('school','divination')
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S','DF'])
        spells.Spell.__init__(self,name,**params)
        
        self.radius = 12
        self.caster_pos = None
        self.reset_time = 15    # time in seconds after caster chooses cone that the game
                                # asks for next cone. 
        
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
        caster_items = caster.list_items(True)
        holy_symbol = False
        for item in caster_items:
            if 'holy_symbol' in item.type:
                holy_symbol = True
                break
        if not holy_symbol:
            return False
            
        return True
    
#    def complete_allowed_to_cast(self, caster, target, game):
#        # to determine if target is an allowed target
# 
#        allowed = True
#        if not isinstance( target, mobile_object.MobileObject ):
#            allowed = False
#            
#        max_range = 0.5
#        range_to_targ = self.range_to_target(caster, target) 
#        if max_range < range_to_targ:
#            allowed = False
#            
#        map_section_name = caster.map_section
#        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, radius = int(round(range_to_targ))+1):
#            allowed = False
#            
#        return allowed

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        self.caster_pos = caster.pos
        self.choose_first_round_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
        pos = caster.lastOrderedPos
        self.caster_pos = pos
        adj = findAdjTiles(pos[0],pos[1], game.map[caster.map_section])
        for tile in adj:
            allowed_tiles.add(tile)
        return allowed_tiles, allowed_targets
    
    def area_effect_func(self, map_section_name, mappos, game):
        self.tile_set = spells.cone_tiles(mappos, map_section_name, game, self.radius,self.caster_pos)
        return self.tile_set

    def choose_first_round_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
        
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
#        ev = UnblockFreeMoveResultsOnClientEvent()
#        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        if hasattr(self,'caster'):
            self.caster.concentration_data = None

    def effect(self, source, data, game):
        # only executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        tile_set = data['tile set']
        
        if 'expiration time' in data:
            expiration_time = data['expiration time']
        else:
            expiration_time = game.Time + 600 * 1000 * self.find_caster_level(caster) + 1
        extra = [expiration_time, caster.pos, data, game.Time]
            
        aura_list = self.find_auras(game, tile_set)   
            
        if data['round'] == 1:
            detect_msg = 'Detect Good spell, round 1 result:'
            if aura_list:
                detect_msg += '\n' + 'Good present'
            else:
                detect_msg += '\n' + 'No good detected'
            other_data_client = [source, 'choose_round_2_action', extra]
        elif data['round'] == 2:
            detect_msg = 'Detect Good spell, round 2 result:'
            num_found = len(aura_list)
            strongest_aura = None
            strongest_aura_number = 0
            for aura in aura_list:
                if aura_dict[aura[1]] > strongest_aura_number:
                    strongest_aura = aura[1]
            if num_found == 0:
                detect_msg += '\n' + 'No good detected'
            else:
                detect_msg += '\n' + str(num_found) + ' good things found.\n'
                detect_msg += 'Most powerful aura is ' + strongest_aura + '.'
            other_data_client = [source, 'choose_round_3_action', extra]
            
        elif data['round'] == 3:
            detect_msg = 'Detect Good spell, round 3 result:'
            if not aura_list:
                detect_msg += '\n' + 'No good detected'
            else:
                for aura in aura_list:
                    pos = aura[0]
                    pos_str = ' North ' + str(caster.pos[1] - pos[1]) + ' squares and East ' + str(pos[0] - caster.pos[0]) + ' squares.' 
                    detect_msg += '\n' + aura[1] + ' aura.' + pos_str
            other_data_client = [source, 'choose_round_1_action', extra]
        orddats.append(['game', 'show message', detect_msg])
        
#        Structure of an event entry in timed_event_lists:
#        (subphase, execution time, event details)
#        
#        Structure of event details:
#        [object_id, event type, anything else]
        
        if game.move_mode == 'phased':
            orddats.append([caster.id, 'add spell concentration data', other_data_client])
        else:
            reset_time = game.Time + self.reset_time * 1000
            effects_timed_event_list.append( (caster.subphase-1, reset_time, [None, 'create orddat entry', [caster.id, 'call function before orders', other_data_client]]) )
#            effects_timed_event_list.append( (caster.subphase-1, reset_time, [caster.id, 'client call function', other_data_client]) )
            
        return orddats

    def find_auras(self, game, tile_set):
        aura_list = []
        objlist = game.objectIdDict.itervalues()
        for obj in objlist:
            if not hasattr(obj, 'carried') \
            or (hasattr(obj, 'carried') and not obj.carried):
                if obj.pos in tile_set:
                    if 'good' in obj.alignment:
                        aura = find_aura_power(obj)
                        if aura:
                            aura_list.append((obj.pos,aura))
                    for effect_entry in obj.temporary_effects:
                        effect = effect_entry[0]
                        e_source = effect[2]
                        if 'spell_name' in e_source:
                            spell = game.complete_dict_of_spells[e_source['spell_name']]
                            if 'good' in spell.descriptors:
                                aura = find_spell_aura_power(spell, e_source, game)
                                if aura:
                                    aura_list.append((obj.pos,aura))
                    obj_items = obj.list_items(True)
                    for item in obj_items:
                        if 'good' in item.alignment:
                            aura = find_aura_power(item)
                            if aura:
                                aura_list.append((obj.pos,aura))
                        for effect_entry in item.temporary_effects:
                            effect = effect_entry[0]
                            e_source = effect[2]
                            if 'spell_name' in e_source:
                                spell = game.complete_dict_of_spells[e_source['spell_name']]
                                if 'good' in spell.descriptors:
                                    aura = find_spell_aura_power(spell, e_source, game)
                                    if aura:
                                        aura_list.append((obj.pos,aura))
        return aura_list
        
    def choose_round_2_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 2nd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_2_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_2_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_2_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_2_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 2
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_3_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 3rd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_3_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_3_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_3_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_3_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 3
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_1_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
            msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
            ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_round_1_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
            queue.put(ev)

    def create_round_1_order(self, caster, target, game):
#        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
class DetectUndead(spells.Spell):
    def __init__(self, **params):
        name = 'detect_undead'
        params.setdefault('display_name', 'Detect Undead')
        params.setdefault('long_desc', "You can sense the presence of undead creatures. The amount of information revealed depends on \
how long you study a particular area or subject. \n\
    1st Round: Presence or absence of undead auras. \n\
    2nd Round: Number of undead auras in the area and the power of the most potent undead aura present. \n\
    3rd Round: The power and location of each aura. If an aura is outside your line of sight, then you discern its direction but \
               not its exact location. \n\
Aura Power: An undead aura's power depends on the HD of the creature.\n\
If cast during phased mode each round you will get to choose whether to concentrate on the same area (thereby allowing progression to 2nd \
or 3rd round), or choose a new cone of detection. Either requires a standard action. \n\
If cast during free move mode, you will get to choose a cone of detection every 15 sec or when \
you have no other orders pending, whichever occurs later.  If more than 30 sec have passed since previous detection, then it is decreed \
that you didn't concentrate on the spell and it ends.  If you are at the same location when the choice appears and less than 30 sec \
have passed since previous detection, then you will get the option of continuing to concentrate on the same area (thereby allowing \
progression to 2nd or 3rd round).")
        params.setdefault('school','divination')
        params.setdefault('classes',{'cleric':1,'paladin':1,'sorcerer':1,'wizard':1})
        params.setdefault('components', ['V','S'])
        spells.Spell.__init__(self,name,**params)
        
        self.radius = 12
        self.caster_pos = None
        self.reset_time = 15    # time in seconds after caster chooses cone that the game
                                # asks for next cone (in free move mode). 
        
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
#        caster_items = caster.list_items(True)
#        holy_symbol = False
#        for item in caster_items:
#            if 'holy_symbol' in item.type:
#                holy_symbol = True
#                break
#        if not holy_symbol:
#            return False
            
        return True
    
#    def complete_allowed_to_cast(self, caster, target, game):
#        # to determine if target is an allowed target
# 
#        allowed = True
#        if not isinstance( target, mobile_object.MobileObject ):
#            allowed = False
#            
#        max_range = 0.5
#        range_to_targ = self.range_to_target(caster, target) 
#        if max_range < range_to_targ:
#            allowed = False
#            
#        map_section_name = caster.map_section
#        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, radius = int(round(range_to_targ))+1):
#            allowed = False
#            
#        return allowed

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        self.caster_pos = caster.pos
        self.choose_first_round_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
        pos = caster.lastOrderedPos
        self.caster_pos = pos
        adj = findAdjTiles(pos[0],pos[1], game.map[caster.map_section])
        for tile in adj:
            allowed_tiles.add(tile)
        return allowed_tiles, allowed_targets
    
    def area_effect_func(self, map_section_name, mappos, game):
        self.tile_set = spells.cone_tiles(mappos, map_section_name, game, self.radius,self.caster_pos)
        return self.tile_set

    def choose_first_round_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
        
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
#        ev = UnblockFreeMoveResultsOnClientEvent()
#        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        if hasattr(self,'caster'):
            self.caster.concentration_data = None

    def effect(self, source, data, game):
        # only executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        tile_set = data['tile set']
        
        if 'expiration time' in data:
            expiration_time = data['expiration time']
        else:
            expiration_time = game.Time + 60 * 1000 * self.find_caster_level(caster) + 1
        extra = [expiration_time, caster.pos, data, game.Time]
            
        aura_list = self.find_auras(game, tile_set)   
            
        if data['round'] == 1:
            detect_msg = 'Detect Undead spell, round 1 result:'
            if aura_list:
                detect_msg += '\n' + 'Undead present'
            else:
                detect_msg += '\n' + 'No undead detected'
            other_data_client = [source, 'choose_round_2_action', extra]
        elif data['round'] == 2:
            detect_msg = 'Detect Undead spell, round 2 result:'
            num_found = len(aura_list)
            strongest_aura = None
            strongest_aura_number = 0
            for aura in aura_list:
                if aura_dict[aura[1]] > strongest_aura_number:
                    strongest_aura = aura[1]
            if num_found == 0:
                detect_msg += '\n' + 'No undead detected'
            else:
                detect_msg += '\n' + str(num_found) + ' undead creatures found.\n'
                detect_msg += 'Most powerful aura is ' + strongest_aura + '.'
            other_data_client = [source, 'choose_round_3_action', extra]
            
        elif data['round'] == 3:
            detect_msg = 'Detect Undead spell, round 3 result:'
            if not aura_list:
                detect_msg += '\n' + 'No undead detected'
            else:
                for aura in aura_list:
                    pos = aura[0]
                    pos_str = ' North ' + str(caster.pos[1] - pos[1]) + ' squares and East ' + str(pos[0] - caster.pos[0]) + ' squares.' 
                    detect_msg += '\n' + aura[1] + ' aura.' + pos_str
            other_data_client = [source, 'choose_round_1_action', extra]
        orddats.append(['game', 'show message', detect_msg])
        
#        Structure of an event entry in timed_event_lists:
#        (subphase, execution time, event details)
#        
#        Structure of event details:
#        [object_id, event type, anything else]
        
        if game.move_mode == 'phased':
            orddats.append([caster.id, 'add spell concentration data', other_data_client])
        else:
            reset_time = game.Time + self.reset_time * 1000
            effects_timed_event_list.append( (caster.subphase-1, reset_time, [None, 'create orddat entry', [caster.id, 'call function before orders', other_data_client]]) )
#            effects_timed_event_list.append( (caster.subphase-1, reset_time, [caster.id, 'client call function', other_data_client]) )
            
        return orddats

    def find_auras(self, game, tile_set):
        aura_list = []
        objlist = game.objectIdDict.itervalues()
        for obj in objlist:
            if not hasattr(obj, 'carried') \
            or (hasattr(obj, 'carried') and not obj.carried):
                if obj.pos in tile_set:
                    if 'undead' == obj.type:
                        aura = find_undead_aura_power(obj)
                        if aura:
                            aura_list.append((obj.pos,aura))
        return aura_list
        
    def choose_round_2_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 2nd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_2_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_2_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_2_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_2_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 2
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_3_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
#            self.game = game
            if caster.pos == extra[1]:
        
                data = {}
                data['title'] = 'Choose an option'
                data['choices'] = []
                data['choices'].append('Concentrate on same area for 3rd round information')
                data['choices'].append('Choose a new area for 1st round information')
                data['choices'].append('Cancel spell')
                ev = ShowDefaultChoicePopup(data,self.round_3_choice_made)
                queue.put(ev)
            else:
                self.choose_round_1_action(source, extra)

    def round_3_choice_made(self, choice_made):
        if choice_made == 0:
            self.create_round_3_order()
        elif choice_made == 1:
            self.choose_round_1_action(self.source, self.extra)
        elif choice_made == 2:
            self.cancel_spellcast()
        
    def create_round_3_order(self):
        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.extra[2]['tile set'])
        data['round'] = 3
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def choose_round_1_action(self, source, extra):
        # extra is a list [expiration_time, caster.pos, data, last detect time, game]
        game = extra[4]
        if game.Time - extra[3] < 30000 and game.Time < extra[0]:
#            source = c_data[0]
            caster_id = source['obj_id']
            caster = game.objectIdDict[caster_id]
            self.caster = caster
            self.source = source
            self.extra = extra
            msg = 'Right click to choose cone area for ' + self.display_name + ' (will be 1st round level of information).'
            ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_round_1_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
            queue.put(ev)

    def create_round_1_order(self, caster, target, game):
#        game = self.extra[4]
        if game:
            if game.move_mode == 'phased':
                self.caster.update_actions_used('use_standard_action')
        data = {}
        data['tile set'] = deepcopy(self.tile_set)
        data['round'] = 1
        data['expiration time'] = self.extra[0]
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
class DivineFavor(spells.Spell):
    def __init__(self, **params):
        name = 'divine_favor'
        params.setdefault('display_name', 'Divine Favor')
        params.setdefault('long_desc', "Calling upon the strength and wisdom of a deity, you gain a \
+1 luck bonus on attack and weapon damage rolls for every three caster levels you have (at least +1, \
maximum +3). The bonus doesn't apply to spell damage.")
        params.setdefault('school','evocation')
        params.setdefault('classes',{'cleric':1, 'paladin':1})
        params.setdefault('components', ['V','S','DF'])
        spells.Spell.__init__(self,name,**params)
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
        caster_items = caster.list_items(True)
        holy_symbol = False
        for item in caster_items:
            if 'holy_symbol' in item.type:
                holy_symbol = True
                break
        if not holy_symbol:
            return False
            
        return True
    
    def selected(self, caster, advclass, game, move_mode = 'phased'):
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.create_order(caster, advclass, game)

#    def find_all_valid_targets(self, source, game):
#        caster_id = source['obj_id']
#        caster = game.objectIdDict[caster_id]
#
#        allowed_tiles = set()
#        allowed_targets = set()
#        allowed_tiles.add(caster.pos)
#        return allowed_tiles, allowed_targets
#    
#    def area_effect_func(self, map_section_name, mappos, game):
#        tile_set = spells.burst_tiles(mappos, map_section_name, game, self.radius)
#        return tile_set
#
#    def choose_target(self, caster, advclass):
#        self.source['obj_id'] = caster.id
#        self.source['spell_name'] = self.name
#        self.source['spell_as_class'] = advclass
#        msg = 'Right click to choose target for ' + self.display_name
#        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
#        queue.put(ev)
                
    def create_order(self, caster, advclass, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        data = {}
#        data['target'] = target.id
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        self.source = {}
        
    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        
#        target_id = data['target']
#        target = game.objectIdDict[target_id]
        expiration_time = game.Time + 60 * 1000 + 1
        effect_details = ['Divine Favor', expiration_time, source]

        effect_func_str_dict = {}
        effect_func_str_dict['bonus'] = ['find_bonus']
        caster.add_temporary_effect(effect_details, game, effect_func_str_dict)
        orddats.append([caster.id, 'add effect', effect_details, effect_func_str_dict])
        effects_timed_event_list.append( (caster.subphase+1, expiration_time, [caster.id, 'effect_expiring', effect_details]) )
        
        return orddats
        
    def find_bonus(self, effect_details, obj, game, value_being_checked = None, reason_for_check = None):
        # source contains information about what is causing the bonus check
        # I'm not sure I can anticipate all the sources.  Try a dict.  See spells.py
        bonus_data = None
        caster_level = self.find_caster_level(obj)
        if caster_level >= 9:
            bonus = 3
        elif caster_level >= 6:
            bonus = 2
        else:
            bonus = 1
        if value_being_checked[0] == 'tohit':
            bonus_data = ['luck', bonus]
        elif value_being_checked[0] == 'damage':
            if reason_for_check:    
                if 'spell_name' not in reason_for_check:
                    if 'attack_type' in reason_for_check:
                        if reason_for_check['attack_type'] == 'melee' or reason_for_check['attack_type'] == 'ranged':
                            bonus_data = ['luck', bonus]
        return bonus_data
        
       
class Doom(spells.Spell):
    def __init__(self, **params):
        name = 'doom'
        params.setdefault('display_name', 'Doom')
        params.setdefault('long_desc', "This spell fills a single subject with a feeling of horrible dread that \
causes it to become shaken.")
        params.setdefault('school','necromancy')
        params.setdefault('descriptors', ['fear','mind-affecting'])
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S','DF'])
        spells.Spell.__init__(self,name,**params)
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if game.move_mode != 'phased':
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
        caster_items = caster.list_items(True)
        holy_symbol = False
        for item in caster_items:
            if 'holy_symbol' in item.type:
                holy_symbol = True
                break
        if not holy_symbol:
            return False
            
        return True

    def complete_allowed_to_cast(self, caster, target, game):
        # requires target
#        allowed = self.basic_allowed_to_cast(caster, game)
        if not isinstance( target, mobile_object.MobileObject ):
            return False
        
        max_range = 20 + int(2*self.find_caster_level(caster))
        range_to_targ = self.range_to_target(caster, target) 
        if max_range < range_to_targ:
            return False
            
        map_section_name = caster.map_section
        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, reason = {'obj_id':caster.id}):
            return False
            
        return True
    

    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # anything that happens when this spell is selected
        # to be cast
        
        # default is to append order with extra data of:
        # target.id
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.choose_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section

        allowed_tiles = set()
        allowed_targets = set()
        idlist = []
        idlist.extend(game.map_data[map_section_name]['monsters'])
        idlist.extend(game.charnamesid.itervalues())
        for id in idlist:
            obj = game.objectIdDict[id]
            if self.complete_allowed_to_cast(caster, obj, game):
#                allowed_tiles.add(obj.pos)
                allowed_targets.add(obj)
        return allowed_tiles, allowed_targets
    
    def choose_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose target for ' + self.display_name
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        caster.update_actions_used('use_standard_action')
        data = {}
        data['target'] = target.id
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        target_id = data['target']
        target = game.objectIdDict[target_id]
#        source = {}
#        source['obj_id'] = caster_id
            
        DC = self.find_spell_DC(caster, source, game)
        if not hgc.made_saving_throw(target_id, 'will', DC, source, game):
            if hgc.passed_spell_resistance(caster,target,self,source,game):            
                expiration_time = game.Time + (60*1000*self.find_caster_level(caster)) + 1
                source['condition_name'] = 'shaken'
                effect_details = ['Shaken', expiration_time, source]
                effect_func_str_dict = game.dict_of_conditions['shaken'].effect_func_str_dict
                target.add_temporary_effect(effect_details, game, effect_func_str_dict)
                orddats.append([target_id, 'add effect', effect_details, effect_func_str_dict])
                effects_timed_event_list.append( (caster.subphase+1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
        
        return orddats
        
class EntropicShield(spells.Spell):
    def __init__(self, **params):
        name = 'entropic_shield'
        params.setdefault('display_name', 'Entropic Shield')
        params.setdefault('long_desc', "A magical field appears around you, glowing with \
a chaotic blast of multicolored hues. This field deflects incoming arrows, rays, and other \
ranged attacks. Each ranged attack directed at you for which the attacker must make an \
attack roll has a 20% miss chance (similar to the effects of concealment). Other attacks \
that simply work at a distance are not affected.")
        params.setdefault('school','abjuration')
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S'])
        spells.Spell.__init__(self,name,**params)
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
            
        return True
    
    def selected(self, caster, advclass, game, move_mode = 'phased'):
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.create_order(caster, advclass, game)

    def create_order(self, caster, advclass, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        data = {}
        source = deepcopy(self.source)
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        self.source = {}
        
    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        
#        target_id = data['target']
#        target = game.objectIdDict[target_id]
        expiration_time = game.Time + 60 * 1000 * self.find_caster_level(caster) + 1
        effect_details = ['Entropic Shield', expiration_time, source]

        effect_func_str_dict = {}
        effect_func_str_dict['bonus'] = ['find_bonus']
        caster.add_temporary_effect(effect_details, game, effect_func_str_dict)
        orddats.append([caster.id, 'add effect', effect_details, effect_func_str_dict])
        effects_timed_event_list.append( (caster.subphase+1, expiration_time, [caster.id, 'effect_expiring', effect_details]) )
        
        return orddats
        
    def find_bonus(self, effect_details, obj, game, value_being_checked = None, reason_for_check = None):
        # source contains information about what is causing the bonus check
        # I'm not sure I can anticipate all the sources.  Try a dict.  See spells.py
        bonus_data = None
        if value_being_checked[0] == 'miss chance':
            if reason_for_check and type(reason_for_check) is dict:
                if 'attack_type' in reason_for_check:
                    attack_type = reason_for_check['attack_type']
                    if attack_type == 'ranged' or attack_type == 'ranged touch':
                        bonus_data = ['entropic shield', 20.0]
        return bonus_data
        
class HideFromUndead(spells.Spell):
    def __init__(self, **params):
        name = 'hide_from_undead'
        params.setdefault('display_name', 'Hide From Undead')
        params.setdefault('long_desc', "Undead cannot see, hear, or smell creatures warded by this \
spell. Even extraordinary or supernatural sensory capabilities, such as blindsense, blindsight, scent, \
and tremorsense, cannot detect or locate warded creatures. Nonintelligent undead creatures (such as \
skeletons or zombies) are automatically affected and act as though the warded creatures are not there. \
An intelligent undead creature gets a single Will saving throw. If it fails, the subject can't see any \
of the warded creatures. If it has reason to believe unseen opponents are present, however, it can \
attempt to find or strike them. If a warded creature attempts to channel positive energy, turn or \
command undead, touches an undead creature, or attacks any creature (even with a spell), the spell \
ends for all recipients.")
        params.setdefault('school','abjuration')
        params.setdefault('classes',{'cleric':1})
        params.setdefault('components', ['V','S','DF'])
        spells.Spell.__init__(self,name,**params)
        
        self.radius = 4
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # to determine if this spell will show up in list of
        # spells to choose from
        
        if self.name not in caster.spells_memorized[as_class]:
            return False
        if 'standard' not in caster.find_allowed_actions():
            return False
        if not caster.can_speak(game):
            return False
        if not caster.can_do_cast_somatics(game):
            return False
        caster_items = caster.list_items(True)
        holy_symbol = False
        for item in caster_items:
            if 'holy_symbol' in item.type:
                holy_symbol = True
                break
        if not holy_symbol:
            return False
            
        return True
    
    def selected(self, caster, advclass, game, move_mode = 'phased'):
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        self.choose_target(caster, advclass)

    def find_all_valid_targets(self, source, game):
#        map_section_name = caster.map_section
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]

        allowed_tiles = set()
        allowed_targets = set()
#        idlist = []
#        idlist.extend(game.map_data[map_section_name]['monsters'])
#        idlist.extend(game.charnamesid.itervalues())
#        for id in idlist:
#            obj = game.objectIdDict[id]
#            if self.complete_allowed_to_cast(caster, obj, game):
##                allowed_tiles.add(obj.pos)
#                allowed_targets.add(obj)
        allowed_tiles.add(caster.pos)
        return allowed_tiles, allowed_targets
    
    def area_effect_func(self, map_section_name, mappos, game):
        tile_set = spells.burst_tiles(mappos, map_section_name, game, self.radius)
        return tile_set

    def choose_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Right click to choose target for ' + self.display_name
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast, area_effect_func = self.area_effect_func)
        queue.put(ev)
                
    def create_order(self, caster, target, game):
        if game:
            if game.move_mode == 'phased':
                caster.update_actions_used('use_standard_action')
        data = {}
#        data['target'] = target.id
        source = deepcopy(self.source)
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)

    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        
        orddats = []
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        map_section_name = caster.map_section
        
#        target_id = data['target']
#        target = game.objectIdDict[target_id]
        expiration_time = game.Time + 600 * 1000 * self.find_caster_level(caster) + 1
        effect_details = ['Hide From Undead', expiration_time, source]

        origin = caster.pos
        
#        loe_tiles = view_utils.find_loe_tiles_from_position_within_radius(origin, caster.map_section, game, self.radius)
        loe_tiles = spells.burst_tiles(origin, map_section_name, game, self.radius)
        loe_tiles.add(origin)
        if caster.objtype == 'playerchar':
            idlist = game.charnamesid.itervalues()
        elif caster.objtype == 'monster':
            idlist = game.map_data[map_section_name]['monsters']
            
        friendly_ids_warded = []
        for id in idlist:
            friend = game.objectIdDict[id]
            if friend.pos in loe_tiles:
                friendly_ids_warded.append(id)
                
        effect_details.append([friendly_ids_warded,[],[]])     # variable data.  First entry is to track
                                                # those allies that received spell (and that thus might
                                                # lose it if anybody does something to break spell.
                                                # 2nd entry is to track enemy ids that have attempted will
                                                # save already.
                                                # 3rd entry is to track enemy ids that have succeeded
                                                # on will save already.
        for id in friendly_ids_warded:
            effect_func_str_dict = {}
            effect_func_str_dict['binary'] = ['find_binary']
            effect_func_str_dict['triggered'] = ['lose_hide']
            friend = game.objectIdDict[id]
            friend.add_temporary_effect(effect_details, game, effect_func_str_dict)
            orddats.append([friend.id, 'add effect', effect_details, effect_func_str_dict])
            effects_timed_event_list.append( (caster.subphase+1, expiration_time, [friend.id, 'effect_expiring', effect_details]) )
        
        return orddats
        
#    def do_host_roll(self, effect_details, game, orddat, reason_for_check = None):
#        if reason_for_check:
#            if 'reason' in reason_for_check:
#                if 'perception' in reason_for_check['reason']:
#                    if 'obj_id' in reason_for_check:
#                        obj_id = reason_for_check['obj_id']
#                        variable_data = effect_details[3]
#                        if obj_id not in variable_data[1]:
#                            source = effect_details[2]
#                            caster = game.objectIdDict[source['obj_id']]
#                            variable_data[1].append(obj_id)
#                            DC = self.find_spell_DC(caster, source, game)
#                            reason_for_throw = {}
#                            reason_for_throw['obj_id'] = caster.id
#                            reason_for_throw['reason'] = [self.display_name]
#                            if hgc.made_saving_throw(obj_id, 'will', DC, reason_for_throw, game):
#                                variable_data[2].append(obj_id)
        
    def find_binary(self, effect_details, obj, game, binary_question, reason_for_check = {}):
        if binary_question == 'detectable_by_undead':
            if reason_for_check:    
                if 'obj_id' in reason_for_check:
                    undead_obj_id = reason_for_check['obj_id']
                    variable_data = effect_details[3]
                    source = effect_details[2]
                    caster = game.objectIdDict[source['obj_id']]
                    ids_of_enemy_will_saves = variable_data[1]
                    if undead_obj_id not in ids_of_enemy_will_saves:
                        ids_of_enemy_will_saves.append(undead_obj_id)
                        DC = self.find_spell_DC(caster, source, game)
                        reason_for_throw = {}
                        reason_for_throw['obj_id'] = caster.id
                        reason_for_throw['reason'] = [self.display_name]
                        if hgc.made_saving_throw(undead_obj_id, 'will', DC, reason_for_throw, game):
                            variable_data[2].append(undead_obj_id)
                        else:
                            return False
                    elif undead_obj_id not in variable_data[2]:
                        return False
        return True
        
    def lose_hide(self, effect_details, obj, game, trigger, reason_for_check = {}):
        
        lost_hide = False
        if trigger == 'attack':
            lost_hide = True
        elif trigger == 'cast spell':
            if 'spell_name' in reason_for_check:
                spell_name = reason_for_check['spell_name']
                if spell_name in spells.spells_using_positive_energy \
                or spell_name == 'command_undead':
                    lost_hide = True
        elif trigger == 'channel energy':
            lost_hide = True
            
        if lost_hide:
            variable_data = effect_details[3]
            for id in variable_data[0]:
                friend = game.objectIdDict[id]
                hgc.premature_loss_of_effect(friend, effect_details)
                
            
        



        

        