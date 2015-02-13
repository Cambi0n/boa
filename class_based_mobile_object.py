import mobile_object as mobj
import weapon
import game_object as gobj
import gamefunctions as gmfnc
from copy import deepcopy


class ClassBasedMobj(mobj.MobileObject):
    
    def __init__(self, advclass, **params):
        # advclass is a dict with class name as key, level in that class as value
        
#        params.setdefault('type', 'adventurer')
        params.setdefault('max_hit_points', 35)
        params.setdefault('base_hit_points', 35)
        params.setdefault('weight', 160)
        params.setdefault('material', 'flesh')
#        params.setdefault('name', name)
#        params.setdefault('objtype', 'playerchar')
        params.setdefault('armor_class', 14)
#        params.setdefault('exp',0)
        
#        params.setdefault('spells_known',['magic_missile'])
#        params.setdefault('spells_memorized',['magic_missile'])
#        self.exp = params['exp']

        mobj.MobileObject.__init__(self,**params)
        
#        self.objtype = 'playerchar'
#        self.name = name
        params.setdefault('spells_known',{})    # keys are advclasses, value is a list of spells known under that class
        self.spells_known = params['spells_known']
        params.setdefault('spells_memorized',{})
        self.spells_memorized = params['spells_memorized']
        params.setdefault('race',None)
        self.race = params['race']


        self.advclasses = advclass
        self.total_level = 1
        
    def find_base_attack_bonuses(self, enemy_obj):
        # this will be based on class
        # will list all modifiers for full attack
        return [0]
    
    def calc_melee_tohit_bonus(self, enemy_obj, game, source):
        # will be based on str, dex, size, etc.
        # doesn't include class based attack bonus
        bonus = 0
        bonus += self.find_total_effect_bonus('tohit', game = game, source = source)
        return bonus
    
    def calc_melee_damage_bonus(self, enemy_obj, game, source):
        # will be based on str, dex, size, etc.
        bonus = find_ability_bonus('str')
        if 'attack_hands' in source and source['attack_hands'] == 'bothhands':
            bonus = int(1.5*bonus)
        bonus += self.find_total_effect_bonus('damage', game = game, source = source)
        return bonus
    
    def find_total_level(self):
        tot_lvl = 0
        for lvl in self.advclasses.itervalues():
            tot_lvl += lvl
        return tot_lvl
    
