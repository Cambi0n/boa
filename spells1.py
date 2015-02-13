
import random
from copy import deepcopy

from events import *
from internalconstants import *
from userconstants import *
import spells
import view_utils
import mobile_object
import hostgamecalcs as hgc

class MagicMissile(spells.Spell):
    def __init__(self, **params):
        name = 'magic_missile'
        params.setdefault('display_name', 'Magic Missile')
        params.setdefault('long_desc', "A missile of magical energy darts forth from your fingertip and \
strikes its target, dealing 1d4+1 points of force damage.  The missile strikes unerringly, even if the target is in melee")
        params.setdefault('school','evocation')
        params.setdefault('descriptors', ['force'])
        params.setdefault('classes',{'wizard':1,'sorcerer':1})
        spells.Spell.__init__(self,name,**params)
        
        self.targets = []
#        self.source = {}
        self.num_targets = ''
        
    def basic_allowed_to_cast(self, caster, as_class, game):
        # doesn't require target
        # to determine if target is an allowed target
        # so that this spell will show up in list of
        # spells to choose from
        
#        allowed = True
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
            
        max_range = 20 + 2*self.find_caster_level(caster)
        range_to_targ = self.range_to_target(caster, target) 
        if max_range < range_to_targ:
            return False
            
        map_section_name = caster.map_section
        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, reason = {'obj_id':caster.id}):
            return False
            
        return True
    
    def selected(self, caster, advclass, game, move_mode = 'phased'):
        # first function called when this spell is selected
        # to be cast
        
        ev = HidePrimaryFloatingMenuEvent()
        queue.put(ev)
        ev = HideSecondaryFloatingMenuEvent()
        queue.put(ev)
        
        caster_level = self.find_caster_level(caster)
        if caster_level >= 9:
            self.num_targets = 'five'
        elif caster_level >= 7:
            self.num_targets = 'four'
        elif caster_level >= 5:
            self.num_targets = 'three'
        elif caster_level >= 3:
            self.num_targets = 'two'
        else:
            self.num_targets = 'one'

        self.choose_first_target(caster, advclass)
        
#            
#        for targ_num in range(num_targets):
#            if targ_num != 0:
#                msg = 'Choose target #' + str(targ_num+1) + ' by right clicking.'
#                ev = ShowChooseTargetInterfaceEvent(msg, caster, self.validate_multiple_target, self.target_chosen)
#                queue.put(ev)
#                # put up non-modal info saying choose a target
#                # with a right click
#            else:
#                self.target_chosen(caster, target)
#                caster.update_actions_used('use_standard_action')
                    
#    def validate_multiple_target(self, caster, target, game):
#        allowed = True
#        if not isinstance( target, mobile_object.MobileObject ):
#            allowed = False
#            
#        max_range = 20 + 2*self.find_caster_level(caster)
#        range_to_targ = self.range_to_target(caster, target) 
#        if max_range < range_to_targ:
#            allowed = False
#            
#        map_section_name = caster.map_section
#        if not view_utils.los_between_two_tiles(caster.pos, target.pos, map_section_name, game, radius = int(round(range_to_targ))+1):
#             allowed = False
#            
#        return allowed
    
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

    def choose_first_target(self, caster, advclass):
        self.source['obj_id'] = caster.id
        self.source['spell_name'] = self.name
        self.source['spell_as_class'] = advclass
        msg = 'Choose first target (out of ' + self.num_targets + ') by right clicking.'
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.target1_chosen, self.cancel_spellcast)
        queue.put(ev)
                
    def target1_chosen(self,caster,target,game):
        self.target_chosen(caster,target)
        if self.find_caster_level(caster) >= 3:
            msg = 'Choose second target (out of ' + self.num_targets + ') by right clicking.'
            ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.target2_chosen, self.cancel_spellcast)
            queue.put(ev)
        else:
            self.create_order(caster)
            ev = ClearTargetInterfaceEvent()
            queue.put(ev)
            
    def target2_chosen(self,caster,target,game):
        self.target_chosen(caster,target)
        if self.find_caster_level(caster) >= 5:
            msg = 'Choose third target (out of ' + self.num_targets + ') by right clicking.'
            ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.target3_chosen, self.cancel_spellcast)
            queue.put(ev)
        else:
            self.create_order(caster)
            ev = ClearTargetInterfaceEvent()
            queue.put(ev)
        
    def target3_chosen(self,caster,target,game):
        self.target_chosen(caster,target)
        if self.find_caster_level(caster) >= 7:
            msg = 'Choose fourth target (out of ' + self.num_targets + ') by right clicking.'
            ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.target4_chosen, self.cancel_spellcast)
            queue.put(ev)
        else:
            self.create_order(caster)
            ev = ClearTargetInterfaceEvent()
            queue.put(ev)

    def target4_chosen(self,caster,target,game):
        self.target_chosen(caster,target)
        if self.find_caster_level(caster) >= 9:
            msg = 'Choose fifth target (out of ' + self.num_targets + ') by right clicking.'
            ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.target5_chosen, self.cancel_spellcast)
            queue.put(ev)
        else:
            self.create_order(caster)
            ev = ClearTargetInterfaceEvent()
            queue.put(ev)

    def target5_chosen(self,caster,target,game):
        self.target_chosen(caster,target)
        self.create_order(caster)
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def target_chosen(self, caster, target):
        self.targets.append(target.id)            
        
    def create_order(self, caster):
        caster.update_actions_used('use_standard_action')
        data = {}
        data['targets'] = deepcopy(self.targets)
        source = deepcopy(self.source)
        self.targets = []
        self.source = {}
        ev = AddCastOrderEvent(source, data)
        queue.put(ev)
        
    def cancel_spellcast(self):
        ev = ClearTargetInterfaceEvent()
        queue.put(ev)
        
    def effect(self, source, data, game):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        targets = data['targets']
        caster_id = source['obj_id']
        caster = game.objectIdDict[caster_id]
        
        damage_details_list = [ [1, [1,4], 1, 'force'] ]
        orddats = []
        damage_msg = 'Result from Magic Missile:' 
        for target_id in targets:
            if target_id in game.objectIdDict:      # in case target is no longer present
                target = game.objectIdDict[target_id]
                if hgc.passed_spell_resistance(caster,target,self,source,game):            
                
                    damage_details = {}
                    damage_details['enemy_id'] = target_id
                    damage_details['tohit_roll'] = None
                    damage_details['tohit_bonus'] = None 
                    
                    hgc.roll_for_damage(damage_details_list, target, damage_details, game)
                    hgc.resolve_effects_from_attack('damage_dealt', damage_details, caster, target, game, source)
                    print 'spells1, magic missile', damage_details_list, damage_details
                    
                    damage_msg += '\n' + str(damage_details['damage_total'][0]) + ' points of damage done. Points of damage done. Points of damage done. Points of damage done.'
        orddats.append(['game', 'show message', damage_msg])

    
#            dam_tot_list = damage_details[4]
#            dam_tot = 0
#            for dam in dam_tot_list:
#                dam_tot += dam
#            target.change_current_hit_points(-dam_tot)
#            
#            orddats.append([caster.id, 'damage dealt', damage_details])
#            orddats.append([target.id, 'received damage', damage_details])
        return orddats

class MageArmor(spells.Spell):
    def __init__(self, **params):
        name = 'mage_armor'
        params.setdefault('display_name', 'Mage Armor')
        params.setdefault('long_desc', "An invisible but tangible field of force \
        surrounds the subject of a mage armor spell, providing a +4 armor bonus to \
        AC. Unlike mundane armor, mage armor entails no armor check penalty, arcane \
        spell failure chance, or speed reduction. Since mage armor is made of force \
        armor is made of force, incorporeal creatures can't bypass it the way they do \
        normal armor.")
        params.setdefault('school','conjuration')
        params.setdefault('subschool','creation')
        params.setdefault('descriptors', ['force'])
        params.setdefault('classes',{'wizard':1,'sorcerer':1})
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
        msg = 'Right click to choose target for ' + self.display_name
        ev = ShowChooseTargetInterfaceEvent(msg, self.source, self.find_all_valid_targets, self.create_order, self.cancel_spellcast)
        queue.put(ev)
                
    def create_order(self, caster, target,game):
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
        target_id = data['target']
        target = game.objectIdDict[target_id]
        
#        expiration_time = game.Time + seconds_per_round * 1000 + 1
        expiration_time = game.Time + 3600 * 1000 * self.find_caster_level(caster) + 1

        effect_details = ['Mage Armor', expiration_time, source]
        effect_func_str = {}
        effect_func_str['bonus'] = ['find_bonus']
        target.add_temporary_effect(effect_details, game, effect_func_str)
        
        orddats.append([target_id, 'add effect', effect_details, effect_func_str])
        
#        bonus_details = ['armor_class', 'armor bonus', 4, expiration_time, ('Mage Armor', ('playerchar',caster.id))]
#        target.add_bonus(bonus_details)
#        orddats.append([target_id, 'add bonus', bonus_details])

        effects_timed_event_list.append( (caster.subphase+1, expiration_time, [target_id, 'effect_expiring', effect_details]) )
#        effects_timed_event_list.append( (expiration_time, [target_id, 'bonus_expiring', bonus_details]) )
        
        return orddats
        
    def find_bonus(self, effect_details, obj, game, value_being_checked = None, reason_for_check = None):
        # source contains information about what is causing the bonus check
        # I'm not sure I can anticipate all the sources.  Try a dict
        bonus_data = None
        if value_being_checked[0] == 'armor_class':
            bonus_data = ['armor bonus', 4]
            if reason_for_check:
                if 'attack_type' in reason_for_check:
                    if reason_for_check['attack_type'] == 'touch':
                        incorporeal = False
                        if 'obj_id' in reason_for_check:
                            obj_id = reason_for_check['obj_id']
                            obj = game.objectIdDict[obj_id]
                            if 'incorporeal' in obj.subtype or obj.is_incorporeal(game, reason_for_check):
                                incorporeal = True
                        if not incorporeal:
                            bonus_data = None
            
        return bonus_data
        
        

