import test_me2
# multiple files can be loaded.  Not sure how to use them yet
'''
Not sure if this file will contain anything other than a single class.

A 'refresh_encounter' function within the class would seem to be 
necessary, to change the map, or possibly for other reasons.
Other functions within the class that necessitate a map
change should return a variable indicating this (so main program
can call the refresh function and reset the map or choice dialog).

In order to allow switching between map-based encounters and 
choice based encounters (no map, a situation is presented and
several choices are allowed, with possibly sub-choices based on
the first choice, and then sub-sub-choices, etc.), some variable such as 
active_state = ['map', map_dir, map_file_name] or 
active_state = ['choice', choice_dir, choice_file_name] would
seem to be necessary.

The map file(s) specified will contain much of the data, such as where
players and monsters start, location of all terrain, traps, objects, etc..

The map file will also need to contain function references that are
activated upon certain events.  For example, I imagine that when
monster A is killed, that one's faction among group B (an attribute 
of this encounter class) will be changed by the function that is activated
upon the killing of monster A.  Probable categories for these function
references are: killing monster, death of monster, entering map 
location, outcome of dialog, etc.  These function references will
probably be stored in game.map_data, and then everytime something 
happens, even moving into a square, the game will need to see if there
is a special function that happens.  Results of these special functions
might have to be sent back to host and players.  Although maybe not.
Maybe there will need to be inquiry functions to return, say, the 
level of one's faction with a group.  But how will the game engine
know it needs to query?  Maybe another special function category is
to do something upon first encountering a monster, when monster first 
sees a party member.  This might lead a monster to be neutral or
friendly instead of aggressive, for example.

So how does a player check on the status of certain encounter attributes?
Maybe a list that identifies these attributes, which is fed back to the
main engine, and query functions for them.

When loading a saved encounter, the monsters will need to be placed 
based on game.map_data rather than the map file.


return types:

['change move mode', 'phased']  (or 'free')
['change map section', map_section_name]
['change map', map_name] 

'''

class Encounter():
    def __init__(self):
        self.map_dir = 'map1'
        self.map_name = 'level2.txt'
        self.desc = 'a scary encounter'
        self.active_state = 'map'
        self.checkable_values = {}
        self.checkable_values['Orc Faction'] = 0
        self.internal_values = {}
        
    def check_effect(self, data):
        
        if self.active_state == 'map':
            return self.check_map(data)
        elif self.active_state == 'choice':
            return self.check_choice(data)
            
    def check_map(self, data):
        if data[0] == 'pos' or data[0] == 'kill monster':
            if self.map_name == 'level2.txt':
                return self.check_level2_txt(data)
        elif data[0] == 'time':
            return self.check_time(data)
        elif data[0] == 'check value':
            return self.checkable_values[data[1]]
        
    def check_choice(self, data):
        pass
     
    def check_level2_txt(self, data):
        section_name = data[1]
        if section_name == 'level1':
            return self.check_level1(data)
            
    def check_time(self, data):
        game_time = data[1]
        return []
            
    def check_level1(self, data):
        effect_type = data[0]
        if effect_type == 'pos':
            return self.check_level1_pos(data)
        elif effect_type == 'kill monster':
            return self.check_level1_kill(data)

    def check_level1_pos(self, data):
        pos = data[2]
        obj_data = data[3]
        if pos[1] < 17 and obj_data[0] == 'playerchar':
            return ['change move mode','phased']
        
    def check_level1_kill(self, data):
        pass
        

