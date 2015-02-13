import carried_object

class Armor(carried_object.CarriedObject):
    def __init__(self,**params):
        
        params.setdefault('type','armor')
        params.setdefault('equippable',True)
        params.setdefault('allowed_slots',['chest'])
        params.setdefault('effect_if_equipped',True)
        effect_dict = {}
        effect_dict['bonus'] = 'find_bonus'
        params.setdefault('effect_func_dict',effect_dict)
        
        carried_object.CarriedObject.__init__(self,**params)

        params.setdefault('armor_bonus',0)
        self.armor_bonus = params['armor_bonus']
        
        
#    def assign_id(self, id):
#        self.id = id
#        self.effect_details = [self.id]
        
    def find_bonus(self, obj, game, value_being_checked = None, reason_for_check = None):
        bonus_data = None
        if value_being_checked[0] == 'armor_class':
            bonus_data = ['armor bonus', self.armor_bonus]
            if reason_for_check:
                if 'attack_type' in reason_for_check:
                    if reason_for_check['attack_type'] == 'touch' or reason_for_check['attack_type'] == 'renged touch':
                        bonus_data = None
        return bonus_data
    
