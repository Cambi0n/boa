def dict_of_races():
    race_dict = {}
    race_dict['elf'] = Elf()
#    race_dict['dwarf'] = Dwarf()
#    race_dict['halfling'] = Halfling()
    race_dict['halfelf'] = Halfelf()
    race_dict['human'] = Human()
#    race_dict['gnome'] = Gnome()
    
    return race_dict


class Elf():
    def __init__(self):
        self.name = 'elf'
        self.display_name = 'Elf'
        self.effect_func_str_dict = {}
        self.effect_func_str_dict['bonus'] = ['find_bonus']
#        self.effect_func_str_dict['binary'] = 'find_binary'

    def find_bonus(self, effect_details, obj, game, value_being_checked, reason_for_check):
        bonus_data = None
        if value_being_checked[0] == 'skill':
            if value_being_checked[1] == 'perception':
                bonus_data = ['racial',+2]
        return bonus_data

#    def find_binary(self, effect_details, obj, game, binary_question, reason_for_check):
#        if binary_question == 'can_choose_orders':
#            return False
#        elif binary_question == 'not_fleeing':
#            return False
#        return True

class Halfelf():
    def __init__(self):
        self.name = 'halfelf'
        self.display_name = 'Half-Elf'
        self.effect_func_str_dict = {}
        self.effect_func_str_dict['bonus'] = ['find_bonus']
#        self.effect_func_str_dict['binary'] = 'find_binary'

    def find_bonus(self, effect_details, obj, game, value_being_checked, reason_for_check):
        bonus_data = None
        if value_being_checked[0] == 'skill':
            if value_being_checked[1] == 'perception':
                bonus_data = ['racial',+2]
        return bonus_data

class Human():
    def __init__(self):
        self.name = 'human'
        self.display_name = 'Human'
        self.effect_func_str_dict = {}
        self.effect_func_str_dict['bonus'] = ['find_bonus']
#        self.effect_func_str_dict['binary'] = 'find_binary'

    def find_bonus(self, effect_details, obj, game, value_being_checked, reason_for_check):
        bonus_data = None
#        if value_being_checked[0] == 'skill':
#            if value_being_checked[1] == 'perception':
#                bonus_data = ['racial',+0]
        return bonus_data
#    def find_binary(self, effect_details, obj, game, binary_question, reason_for_check):
#        if binary_question == 'can_choose_orders':
#            return False
#        elif binary_question == 'not_fleeing':
#            return False
#        return True
