
#from events import *
#from internalconstants import *

import game_object
#import mobile_object
import weapon
import carried_object



def create_new_item(data, game = None, id = None):
    # only run by host
    if 'weapon' in data['type']:
        item = weapon.Weapon(**data)
    elif 'carried' in data['type']:
        item = carried_object.CarriedObject(**data)
    else:
        item = game_object.GameObject(**data)
#    elif data['type'] == 'torch' or data['type'] == 'container':
#        item = game_object.GameObject(**data)
        
        
    if id:
        item.assign_id(id)
    else:
        id = game.giveID()
        item.assign_id(id)
            
#    game.objectIdDict[id] = item
    return item
    
def find_item_bonuses(item, bonuses, bonus_func_list, value_being_checked = None, reason_for_check = None, game = None):
    for bonus_func in bonus_func_list:
        bonus_data = bonus_func(None, item, game, value_being_checked = value_being_checked, reason_for_check = reason_for_check)
        if bonus_data:
            bonuses.append(bonus_data)
            
    
    