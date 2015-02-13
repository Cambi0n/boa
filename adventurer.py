import saveload as sl
import mobile_object as mobj
import class_based_mobile_object as cbmobj
import weapon
import game_object as gobj
import gamefunctions as gmfnc
from copy import deepcopy


#class adventurer(mobj.MobileObject):
class adventurer(cbmobj.ClassBasedMobj):
    
    def __init__(self, name, advclass, race, **params):
        
        params.setdefault('type', 'adventurer')
#        params.setdefault('max_hit_points', 35)
#        params.setdefault('current_hit_points', 35)
#        params.setdefault('weight', 160)
#        params.setdefault('material', 'flesh')
        params.setdefault('name', name)
        params.setdefault('objtype', 'playerchar')
#        params.setdefault('armor_class', 14)
        
        params.setdefault('spells_known',{'wizard':['magic_missile', 'mage_armor']})
        params.setdefault('spells_memorized',{'wizard':['magic_missile', 'mage_armor'], \
                                            'cleric': ['cure_light_wounds','detect_chaos','hide_from_undead'] })

        cbmobj.ClassBasedMobj.__init__(self, advclass, **params)

        params.setdefault('exp',0)
        self.exp = params['exp']
        
#        self.advclasses = advclass
        self.race = race
        self.languages_spoken = ['Common', race]
        self.languages_understood = deepcopy(self.languages_spoken)
#        self.total_advlevel = 1

        
    def savetodisk(self,profile):
        sl.savehero(self,profile)
        
    def eval_low_hp(self):
        if self.find_current_hit_points() <= 0:
            if self.find_current_hit_points() == 0:
                self.status -= set(['dying','dead'])
                self.status.add('disabled')
            elif self.find_current_hit_points() > -(self.con + self.find_total_effect_bonus(('con'))):
                self.status -= set(['disabled','dead'])
                self.status.add('dying')
            else:
                self.status -= set(['disabled','dying'])
                self.status.add('dead')
        else:
            self.status -= set(['disabled','dying','dead'])
    

        