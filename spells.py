
import math
import mobile_object
import view_utils

class Spell():
    def __init__(self, name, **params):
        self.name = name
        
        params.setdefault('display_name', name)
        self.display_name = params['display_name']
        params.setdefault('long_desc', '')
        self.long_desc = params['long_desc']
        params.setdefault('school', '')
        self.school = params['school']
        params.setdefault('subschool', '')
        self.subschool = params['subschool']
        params.setdefault('descriptors', [])
        self.descriptors = params['descriptors']
        params.setdefault('classes', {})
        self.classes = params['classes']
        params.setdefault('casting_time', 'standard')
        self.casting_time = params['casting_time']
        params.setdefault('components', ['V','S'])
        self.components = params['components']
        params.setdefault('material_components', [])
        self.material_components = params['material_components']
        
#        params.setdefault('range', {})
#        self.range = params['range']
#        params.setdefault('targets', {})
#        self.targets = params['targets']
        params.setdefault('spell_resistance',True)
        self.spell_resistance = params['spell_resistance']
        params.setdefault('saving_throw',False)
        self.saving_throw = params['saving_throw']
        params.setdefault('needs_loe',True)
        self.needs_loe = params['needs_loe']
        params.setdefault('needs_los',True)
        self.needs_los = params['needs_los']
        params.setdefault('source',{})
        self.source = params['source']
#        params.setdefault('duration',{})
#        self.duration = params['duration']
        
    def basic_allowed_to_cast(self, caster, target, game = None, move_mode = 'phased'):
        # doesn't require target
        # to determine if target is an allowed target
        # so that this spell will show up in list of
        # spells to choose from

        # called from right_click_menus, add_spell_submenu
        
        allowed = True
        if self.name not in caster.spells_memorized:
            allowed = False
        if move_mode != 'phased':
            allowed = False
        if not isinstance( target, mobile_object.MobileObject ):
            allowed = False
        if self.casting_time == 'standard':
            if 'standard' not in caster.find_allowed_actions():
                allowed = False
        elif self.casting_time == 'full':
            if 'full' not in caster.find_allowed_actions():
                allowed = False
        return allowed
    
    def selected(self, caster, target, game = None, move_mode = 'phased'):
        # function called when this spell is selected
        # to be cast
        
        # assigned to click in right_click_menus, add_spell_submenu
        
        if move_mode == 'phased':
            data = {}
            data['target_id'] = target.id
            ev = AddCastOrderEvent(caster.id, self.name, data)
            queue.put(ev)
            
            if self.casting_time == 'full':
                caster.update_actions_used('use_full_round')
            elif self.casting_time == 'standard':
                caster.update_actions_used('use_standard_action')
            
        else:
            self.effect(caster,target)
        
    def effect(self, caster, data, game = None):
        # anything that happens when this spell takes effect
        # I think this will only be executed by hostcomplete
        
        # this needs to actually make chnages to hostcomplete data
        # and then create an outgoing order list that gets
        # sent to each client
        
        # this is called only from hostgamecalcs.cast_spell, which
        # is called from handle_game_timed_events
        
        pass
    
    def range_to_target(self,caster,target):
        cxpos = caster.pos[0]
        cypos = caster.pos[1]
        txpos = target.pos[0]
        typos = target.pos[1]
        return math.sqrt( (txpos - cxpos)**2 + (typos - cypos)**2 )
    
    def find_caster_level(self, caster):
        caster_level = 0
        for c,l in caster.advclasses.iteritems():
            if c in self.classes:
                caster_level += l
        return caster_level        
    
    def find_spell_DC(self, caster, source, game):
        if 'spell_as_class' in source:
            as_class = source['spell_as_class']
        else:
            as_class = 'no_class'
        if as_class in self.classes:
            spell_level = self.classes[as_class]
        else:
            spell_level = 0
        if as_class == 'wizard':
            ability_bonus = caster.find_ability_bonus('int',game)            
        elif as_class in ['bard','paladin','sorcerer']:
            ability_bonus = caster.find_ability_bonus('cha',game)            
        elif as_class in ['cleric','druid','ranger']:
            ability_bonus = caster.find_ability_bonus('wis',game)
        else:
            ability_bonus = 0
                        
        return 10 + spell_level + ability_bonus 

def burst_tiles(pos, map_section_name, game, radius):
    tile_set = view_utils.find_loe_tiles_from_position_within_radius(pos, map_section_name, game, radius)
    tile_set.remove(pos)
    return tile_set

def cone_tiles(pos, map_section_name, game, radius, source_tile):
    # in general, a cone starts from a single tile, but the values allowed for pos
    # will be the 8 tiles surrounding the single source tile.  The cone then goes 
    # from the source out in the direction of pos.
    # Note that my cones (and bursts) are slightly different than those in SRD.
    # Instead of using a tile intersection as origin, I use a tile.  It would be possible
    # to emulate SRD, but it never made much sense to me.  How is its 15' cone consistent
    # with its 30' cone?
    tile_set = view_utils.find_loe_tiles_from_position_within_radius(source_tile, map_section_name, game, radius)
    tile_set.remove(source_tile)
    px = pos[0]
    py = pos[1]
    sx = source_tile[0]
    sy = source_tile[1]
    tiles_to_remove = set()
    if px-sx>0 and py-sy<0:     # top right
        for tile in tile_set:
            if not (tile[0]-sx > 0 and tile[1]-sy < 0):
                tiles_to_remove.add(tile)
    elif px-sx>0 and py-sy>0:     # bottom right
        for tile in tile_set:
            if not (tile[0]-sx > 0 and tile[1]-sy > 0):
                tiles_to_remove.add(tile)
    elif px-sx<0 and py-sy>0:     # bottom left
        for tile in tile_set:
            if not (tile[0]-sx < 0 and tile[1]-sy > 0):
                tiles_to_remove.add(tile)
    elif px-sx<0 and py-sy<0:     # top left
        for tile in tile_set:
            if not (tile[0]-sx < 0 and tile[1]-sy < 0):
                tiles_to_remove.add(tile)
    elif px==sx and py-sy<0:        # top
        for tile in tile_set:
            if not (tile[1]-sy < 0 and abs(tile[0]-sx) < abs(tile[1]-sy)):
                tiles_to_remove.add(tile)
    elif py==sy and px-sx>0:        # right
        for tile in tile_set:
            if not (tile[0]-sx > 0 and abs(tile[1]-sy) < abs(tile[0]-sx)):
                tiles_to_remove.add(tile)
    elif px==sx and py-sy>0:        # bottom
        for tile in tile_set:
            if not (tile[1]-sy > 0 and abs(tile[0]-sx) < abs(tile[1]-sy)):
                tiles_to_remove.add(tile)
    elif py==sy and px-sx<0:        # left
        for tile in tile_set:
            if not (tile[0]-sx < 0 and abs(tile[1]-sy) < abs(tile[0]-sx)):
                tiles_to_remove.add(tile)
                
    tile_set -= tiles_to_remove
    return tile_set
                    
spells_using_positive_energy = ['cure_light_wounds',
                                'cure_light_wounds_mass',
                                'consecration']
    
    
    

'''

'''

'''
temp_effect dictionary keys and possible values
key    values


'''

