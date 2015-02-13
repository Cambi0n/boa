import mobile_object as mobj
import weapon
import gamefunctions as gmfnc
import mobj_actions as mact


class MonsterClass(mobj.MobileObject):
    # for monsters that aren't based on class
    def __init__(self, species, **params):
        
        params.setdefault('max_hit_points', 25)
        params.setdefault('base_hit_points', 25)
        params.setdefault('weight', 160)
        params.setdefault('material', 'flesh')
        params.setdefault('visible', True)  # todo: temproarily make all vis, used any more?
        params.setdefault('armor_class', 12)
#        params['type'] = type
#        params['subtype'] = subtype
        natural_attacks = {'claw': [2, 0, [['1d6', 'slash']] ]}
        params.setdefault('natural_attacks',natural_attacks)
        params.setdefault('languages_understood',['Common'])

        mobj.MobileObject.__init__(self,**params)
        
        self.species = species      # the monster, as in the name given in beastiary entry
        self.monster_type = 'undead'      # will be set based on species
        self.monster_subtype = None      # will be set based on species
        self.objtype = 'monster'
        self.movespeed = 6
        self.alignment = ['chaotic']
        self.num_hit_dice = 5
        
#        self.name = mact.find_unique_monster_display_name(self)
#        self.display_name = self.name
#        self.type = type
#        self.subtype = subtype
        
    def find_base_attack_bonuses(self, enemy_obj):
        # this will be based on monster description
        # will list all modifiers for full attack
        # usually 0?
        # needed so calculations that request this have an entry for non-class-based monsters
        return [0]
    
    def calc_melee_tohit_bonus(self, enemy_obj, game, source):
        # will be based on monster description, typically specified as 2nd entry 
        # in a self.natural_attacks value
        # doesn't include base attack bonuses
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
#        bonus = 0
#        bonus += self.find_total_temporary_effect_bonus('damage', game = game, source = source)
#        return bonus

