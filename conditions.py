


def dict_of_conditions():
    cond_dict = {}
    cond_dict['frightened'] = Frightened()
    cond_dict['shaken'] = Shaken()
    cond_dict['prone'] = Prone()
    
    return cond_dict


class Frightened():
    def __init__(self):
        self.name = 'frightened'
        self.display_name = 'Frightened'
        self.effect_func_str_dict = {}
        self.effect_func_str_dict['bonus'] = ['find_bonus']
        self.effect_func_str_dict['binary'] = ['find_binary']

    def find_bonus(self, effect_details, obj, game, value_being_checked, reason_for_check):
        bonus_data = None
        if value_being_checked[0] == 'tohit':
            bonus_data = ['Frightened',-2]
        if value_being_checked[0] == 'saving_throw':
            bonus_data = ['Frightened',-2]
        if value_being_checked[0] == 'skill':
            bonus_data = ['Frightened',-2]
        if value_being_checked[0] == 'ability_check':
            bonus_data = ['Frightened',-2]
        return bonus_data

    def find_binary(self, effect_details, obj, game, binary_question, reason_for_check):
        if binary_question == 'can_choose_orders':
            return False
        elif binary_question == 'not_fleeing':
            return False
        return True

class Shaken():
    def __init__(self):
        self.name = 'shaken'
        self.display_name = 'Shaken'
        self.effect_func_str_dict = {}
        self.effect_func_str_dict['bonus'] = ['find_bonus']

    def find_bonus(self, effect_details, obj, game, value_being_checked, reason_for_check):
        bonus_data = None
        if value_being_checked[0] == 'tohit':
            bonus_data = ['Shaken',-2]
        if value_being_checked[0] == 'saving_throw':
            bonus_data = ['Shaken',-2]
        if value_being_checked[0] == 'skill':
            bonus_data = ['Shaken',-2]
        if value_being_checked[0] == 'ability_check':
            bonus_data = ['Shaken',-2]
        return bonus_data

class Prone():
    def __init__(self):
        self.name = 'prone'
        self.display_name = 'Prone'
        self.effect_func_str_dict = {}
        self.effect_func_str_dict['bonus'] = ['find_bonus']
        self.effect_func_str_dict['mult'] = ['find_mult']
        self.effect_func_str_dict['binary'] = ['find_binary']

    def find_bonus(self, effect_details, obj, game, value_being_checked, reason_for_check):
        bonus_data = None
        if value_being_checked[0] == 'tohit':
            bonus_data = ['Prone',-4]
        if value_being_checked[0] == 'armor_class':
            if 'attack_type' in reason_for_check:
                attack_type = reason_for_check['attack_type']
                if attack_type == 'melee' or attack_type == 'melee touch':
                    bonus_data = ['Prone',-4]
                if attack_type == 'ranged' or attack_type == 'ranged touch':
                    bonus_data = ['Prone',+4]
        return bonus_data

    def find_binary(self, effect_details, obj, game, binary_question, reason_for_check):
        if binary_question == 'can_run':
            return False
        elif binary_question == 'can_charge':
            return False
        elif binary_question == 'can_take_five_foot_step':
            return False
        elif binary_question == 'not_prone':
            return False
        elif binary_question == 'can_use_sling':
            return False
        elif binary_question == 'can_use_bow':
            return False
        return True

    def find_mult(self, effect_details, obj, game, value_being_checked, reason_for_check):
        bonus_data = None
        if value_being_checked[0] == 'movespeed':
            base_movespeed = obj.movespeed
            new_movespeed = 1.
            mult = new_movespeed / base_movespeed
            bonus_data = ['Prone',mult]
        return bonus_data
    