
from bitarray import bitarray
from collections import deque
from math import *
from copy import deepcopy
from userconstants import *
from gamefunctions import *

MAX_SIGHT = 25
SLOPE_SCALE = 100000
SOURCE_SIGHT_SPOTS = [(0,0), (500,-500),(-500,500), (250, -250), (-250, 250)] 
INTERNAL_HORIZONTAL_SIGHT_SPOT = [2]    # for octant 0 (East South East), which SOURCE_SIGHT_SPOTS
                                        # can serve as a source for a sight ray that is completely
                                        # within the octant (not at the edge of the octant), but also 
                                        # for which a sight ray that travels perfectly horizontally has to 
                                        # be checked for blockage by 2 separate tiles, otherwise the 
                                        # general D&D sight rule will let vision pass along the edges 
                                        # of 2 wall tiles (between 2 joined wall tiles) and through.
INTERNAL_DIAGONAL_SIGHT_SPOT = [1]

vinfo = {}
# D&D sight rule: if any part of source tile can draw a line
# to any part of target tile without an intervening wall,
# then los exists.  Even if only a corner or an edge
# is grazed, los still exists.

# Note that I have decided that if 2 wall tiles touch "kiddie corner",
# (and open tiles along sight line) then sighting can go through this gap.


#SOURCE_SIGHT_SPOTS = [(0,0)] 
#INTERNAL_HORIZONTAL_SIGHT_SPOT = []    # for octant 0 (East South East), which SOURCE_SIGHT_SPOTS

class ViewInfo():
    def __init__(self,x,y,dist):
        
        self.slope_numbers_sight_into = {}      # each entry is a bitarray of slope numbers from 
                                # a spot in source tile to a corner of other
                                # tiles.  The number of entries (bitarrays) will
                                # be equal to SOURCE_SIGHT_SPOTS 
        
        self.slope_numbers_block = {}
        self.four_corner_slopes = {}
        self.horiz_slope_idx = {}
        self.diag_slope_idx = {}
        
        self.grid = []       # the xy duples of this grid for each of the 8 octants
        
        self.adjacent = []    # direction to move to account for sighting
                                    # horizontal or vertical, used with INTERNAL_HORIZONTAL_SIGHT_SPOT
        
        self.next_h = None   # the ViewInfo instance of the next tile horizontally
        self.next_d = None   # the ViewInfo instance of the next tile diagonally

        self.dist = dist    # distance of this tile from source tile
        self.x = x
        self.y = y

def init_view_info_aux(vslopes, vsmin, vsmax, numer, denom, source_idx ):

#    if denom == 0:
#        m = SLOPE_SCALE*2
#    else:
#        m = numer / denom
#    
#    if (m > 0 and m <= SLOPE_SCALE) \
#    or (m == 0 and source_idx in INTERNAL_HORIZONTAL_SIGHT_SPOT):
#    
#        if m not in vslopes:
#            vslopes.append(m)
    if denom == 0:
        m = SLOPE_SCALE*10
    else:
        m = numer / denom
    
    if m not in vslopes:
        vslopes.append(m)
            
    if m < vsmin:
        vsmin = m
    if m > vsmax:
        vsmax = m

    return vsmin, vsmax, m

def init_view_info():
    
#    vinfo = {}
    vinfo['slope_numbers'] = []
    slope_numbers = []
    
    for x in range(MAX_SIGHT+1):
        for y in range(x+1):
#        for y in range(x,MAX_SIGHT+1):
            dist = sqrt(x**2 + y**2)
            if dist <= MAX_SIGHT:
                new_vi = ViewInfo(x,y,dist)
                new_vi.grid.extend([(x,y),(y,x),(-y,x),(-x,y),(-x,-y),(-y,-x),(y,-x),(x,-y)])
                new_vi.adjacent.extend([(0,1),(1,0),(-1,0),(0,1),(0,-1),(-1,0),(1,0),(0,-1)])
#                new_vi.grid.extend([(y,x),(x,y),(x,-y),(y,-x),(-y,-x),(-x,-y),(-x,y),(-y,x)])

                vinfo[(x,y)] = new_vi
                
    for key, this_vi in vinfo.iteritems():
        if key != 'slope_numbers':
            this_x = this_vi.x
            this_y = this_vi.y
            if (this_x + 1,this_y) in vinfo:
                this_vi.next_h = vinfo[(this_x+1,this_y)]
            else:
                this_vi.next_h = vinfo[(0,0)]
            if (this_x + 1,this_y+1) in vinfo:
                this_vi.next_d = vinfo[(this_x+1,this_y+1)]
            else:
                this_vi.next_d = vinfo[(0,0)]
            # is following necessary?
    #        if this_x == this_y:
    #            this_vi.next_h = this_vi.next_d
                
    
    view_slopes = {}

    for source_idx, sight_offset in enumerate(SOURCE_SIGHT_SPOTS):
        view_slopes[source_idx] = []
        four_corners = {}
        view_slopes_min = {}
        view_slopes_max = {}
        s_x_offset = sight_offset[0]
        s_y_offset = sight_offset[1]
        for x in range(MAX_SIGHT+1):  # horizontal and vertical tiles will need special handling
            for y in range(x+1):
#            for y in range(y,MAX_SIGHT+1):
                dist = sqrt(x**2 + y**2)
                if dist <= MAX_SIGHT:
                    view_slopes_min[(x,y)] = SLOPE_SCALE*2
                    view_slopes_max[(x,y)] = 0
                    four_corners[(x,y)] = set()
                    
                    # slope to top right corner
                    numer = SLOPE_SCALE*(1000*y - 500 - s_y_offset)
                    denom = 1000*x + 500 - s_x_offset
                    view_slopes_min[(x,y)], view_slopes_max[(x,y)], m = init_view_info_aux(view_slopes[source_idx], view_slopes_min[(x,y)], view_slopes_max[(x,y)], numer, denom, source_idx)
                    four_corners[(x,y)].add(m)
                    
                    # slope to top left corner
                    numer = SLOPE_SCALE*(1000*y - 500 - s_y_offset)
                    denom = 1000*x - 500 - s_x_offset
                    view_slopes_min[(x,y)], view_slopes_max[(x,y)], m = init_view_info_aux(view_slopes[source_idx], view_slopes_min[(x,y)], view_slopes_max[(x,y)], numer, denom, source_idx)
                    four_corners[(x,y)].add(m)
                    
                    # slope to bottom right corner
                    numer = SLOPE_SCALE*(1000*y + 500 - s_y_offset)
                    denom = 1000*x + 500 - s_x_offset
                    view_slopes_min[(x,y)], view_slopes_max[(x,y)], m = init_view_info_aux(view_slopes[source_idx], view_slopes_min[(x,y)], view_slopes_max[(x,y)], numer, denom, source_idx)
                    four_corners[(x,y)].add(m)

                    # slope to bottom left corner
                    numer = SLOPE_SCALE*(1000*y + 500 - s_y_offset)
                    denom = 1000*x - 500 - s_x_offset
                    view_slopes_min[(x,y)], view_slopes_max[(x,y)], m = init_view_info_aux(view_slopes[source_idx], view_slopes_min[(x,y)], view_slopes_max[(x,y)], numer, denom, source_idx)
                    four_corners[(x,y)].add(m)
                    
        view_slopes[source_idx].sort()
        num_slopes = len(view_slopes[source_idx])
        vinfo['slope_numbers'].append(num_slopes)
        
        for key, this_vi in vinfo.iteritems():
            if key != 'slope_numbers':

                this_vi.slope_numbers_sight_into[source_idx] = bitarray(num_slopes)
                this_vi.slope_numbers_sight_into[source_idx].setall(False)
                this_vi.slope_numbers_block[source_idx] = bitarray(num_slopes)
                this_vi.slope_numbers_block[source_idx].setall(False)
                this_vi.four_corner_slopes[source_idx] = bitarray(num_slopes)
                this_vi.four_corner_slopes[source_idx].setall(False)
                this_vi.horiz_slope_idx[source_idx] = None
                this_vi.diag_slope_idx[source_idx] = None
                x = this_vi.x
                y = this_vi.y
                
                # analyze slopes
                for slope_idx,slope in enumerate(view_slopes[source_idx]):
                    if this_vi.dist > 0:
                        if slope >= view_slopes_min[(x,y)] \
                        and slope <= view_slopes_max[(x,y)]:
                            # >= and <= correct?
                            this_vi.slope_numbers_sight_into[source_idx][slope_idx] = True
                            if slope > view_slopes_min[(x,y)] \
                            and slope < view_slopes_max[(x,y)]:
                                this_vi.slope_numbers_block[source_idx][slope_idx] = True
                        if slope in four_corners[(x,y)]:
                            this_vi.four_corner_slopes[source_idx][slope_idx] = True
                        if slope == 0 and source_idx in INTERNAL_HORIZONTAL_SIGHT_SPOT:
                            this_vi.horiz_slope_idx[source_idx] = slope_idx
                        if slope == SLOPE_SCALE and source_idx in INTERNAL_DIAGONAL_SIGHT_SPOT:
                            this_vi.diag_slope_idx[source_idx] = slope_idx
                            
#    return vinfo

def determine_tiles_illuminated_by_lightsource_old(game, light_source, mapsection_name):
    pos = light_source[0]
#    map_section = game.map[mapsection_name]
    
    light_levels = {}
    if light_source[1] > 0:
        los1_tiles = find_los_tiles_from_position_within_radius(pos, map_section_name, game, light_source[1])
        for tile in los1_tiles:
            light_levels[tile] = BRIGHT_LIGHT_INTENSITY
    else:
        los1_tiles = set()
    if light_source[2] > light_source[1]:
        los2_tiles = find_los_tiles_from_position_within_radius(pos, map_section_name, game, light_source[2])
        losnew_tiles = los2_tiles - los1_tiles 
        for tile in losnew_tiles:
            light_levels[tile] = NORMAL_LIGHT_INTENSITY
    else:
        los2_tiles = set()
    if light_source[3] > light_source[2]:
        los1_tiles = find_los_tiles_from_position_within_radius(pos, map_section_name, game, light_source[3])
        losnew_tiles = los1_tiles - los2_tiles 
        for tile in losnew_tiles:
            light_levels[tile] = DIM_LIGHT_INTENSITY
    else:
        los1_tiles = set()
    if light_source[4] > light_source[3]:
        los2_tiles = find_los_tiles_from_position_within_radius(pos, map_section_name, game, light_source[4])
        losnew_tiles = los2_tiles - los1_tiles 
        for tile in losnew_tiles:
            light_levels[tile] = ULTRADIM_LIGHT_INTENSITY
    return light_levels

def determine_tiles_illuminated_by_lightsource(game, light_source, map_section_name):
    pos = light_source[0]
#    map_section = game.map[mapsection_name]
    light_levels = {}
    
    max_dist = max(light_source[1:])
    max_dist = min(max_dist,MAX_SIGHT)
    squared_distances = []
    for dist in light_source[1:]:
        if dist < 0:
            squared_distances.append(-1)
        else:
            squared_distances.append(dist**2)
    los_tiles, revealed_tiles = find_los_tiles_from_position_within_radius(pos, map_section_name, game, max_dist)
#    for tile in los_tiles:
    for tile in revealed_tiles:
        dist = (pos[0] - tile[0])**2 + (pos[1] - tile[1])**2
        if dist <= squared_distances[0]:
            light_levels[tile] = BRIGHT_LIGHT_INTENSITY
        elif dist <= squared_distances[1]:
            light_levels[tile] = NORMAL_LIGHT_INTENSITY
        elif dist <= squared_distances[2]:
            light_levels[tile] = DIM_LIGHT_INTENSITY
        else:
            light_levels[tile] = ULTRADIM_LIGHT_INTENSITY
    return light_levels

def los_between_two_tiles(source_pos, other_pos, map_section_name, game, reason = {}):
    o2 = determine_octant_of_tile_compared_to_source(source_pos,other_pos)
    dist = sqrt((source_pos[0] - other_pos[0])**2 + (source_pos[1] - other_pos[1])**2)
    radius = int(ceil(dist))
#    vinfo = game.vinfo
    if radius > MAX_SIGHT:
        radius = MAX_SIGHT
    los_tiles, revealed_tiles, sight_line_count = find_los_tiles_in_one_octant(source_pos, map_section_name, game, radius, o2, reason, other_pos)
    los_tiles.add(source_pos)
    if other_pos in los_tiles:
        los_exists = True
    else:
        los_exists = False
    return los_exists

def loe_between_two_tiles(source_pos, other_pos, map_section_name, game, reason = {}):
    o2 = determine_octant_of_tile_compared_to_source(source_pos,other_pos)
    dist = sqrt((source_pos[0] - other_pos[0])**2 + (source_pos[1] - other_pos[1])**2)
    radius = int(ceil(dist))
#    vinfo = game.vinfo
    if radius > MAX_SIGHT:
        radius = MAX_SIGHT
    loe_tiles, effect_line_count = find_loe_tiles_in_one_octant(source_pos, map_section_name, game, radius, o2, reason, other_pos)
    loe_tiles.add(source_pos)
    if other_pos in loe_tiles:
        loe_exists = True
    else:
        loe_exists = False
    return loe_exists

def cover_between_two_tiles(source_pos, other_pos, map_section_name, game, ranged = True, reason = {}):
    # determines whether other_pos has cover from source_pos
    cover = 0
    soft_cover = 0
    if source_pos != other_pos:
        dist = sqrt((source_pos[0] - other_pos[0])**2 + (source_pos[1] - other_pos[1])**2)
        radius = int(ceil(dist))
        if radius > MAX_SIGHT:
            radius = MAX_SIGHT
        o2 = determine_octant_of_tile_compared_to_source(source_pos,other_pos)
        cover, soft_cover = calc_cover_between_two_tiles(source_pos, other_pos, map_section_name, game, radius, o2, ranged, reason)            
    return cover, soft_cover
            
def determine_octant_of_tile_compared_to_source(source,other):
    sx = source[0]
    sy = source[1]
    ox = other[0]
    oy = other[1]
    if ox >= sx:
        if oy >= sy:
            if ox-sx >= oy-sy:
                o2 = 0
#                zeroth_octant_tuple = (ox-sx,oy-sy)
            else:
                o2 = 1
#                zeroth_octant_tuple = (oy-sy,ox-sx)
        else:
            if ox-sx >= -(oy-sy):
                o2 = 7
#                zeroth_octant_tuple = (ox-sx,sy-oy)
            else:
                o2 = 6
#                zeroth_octant_tuple = (sy-oy,ox-sx)
    else:
        if oy >= sy:
            if ox-sx >= -(oy-sy):
                o2 = 2
#                zeroth_octant_tuple = (oy-sy,sx-ox)
            else:
                o2 = 3
#                zeroth_octant_tuple = (sx-ox,oy-sy)
        else:
            if ox-sx >= (oy-sy):
                o2 = 5
#                zeroth_octant_tuple = (sy-oy,sx-ox)
            else:
                o2 = 4
#                zeroth_octant_tuple = (sx-ox,sy-oy)
#    return o2, zeroth_octant_tuple
    return o2

def find_zeroth_octant_tuple(source, other, o2):
    sx = source[0]
    sy = source[1]
    ox = other[0]
    oy = other[1]
    dx = ox - sx
    dy = oy - sy
    if o2 == 0:
        zot = (dx,dy)
    elif o2 == 1:
        zot = (dy,dx)
    elif o2 == 2:
        zot = (dy,-dx)
    elif o2 == 3:
        zot = (-dx,dy)
    elif o2 == 4:
        zot = (-dx,-dy)
    elif o2 == 5:
        zot = (-dy,-dx)
    elif o2 == 6:
        zot = (-dy, dx)
    elif o2 == 7:
        zot = (dx,-dy)
    return zot

def does_tile_block_los(pos, map_section, map_data, source = {}):
    # block_los_beyond_1 is for walls with narrow openings, like arrow slits
    # can only see into tile adjacent to such a wall
    block_los_into = False
    block_los_beyond = False
    block_los_beyond_1 = False
    tile_type = map_section[pos][0]
    if tile_type == 'wall':
        block_los_into = True
        block_los_beyond = True
        block_los_beyond_1 = True
    elif tile_type == 'wall with large opening':
        block_los_into = True
        block_los_beyond = False
        block_los_beyond_1 = False
    elif tile_type == 'wall with small opening':
        block_los_into = True
        block_los_beyond = False
        block_los_beyond_1 = True
        
    if pos in map_data['fog']:
        block_los_beyond = True
        block_los_beyond_1 = True
        
    if pos in map_data['illusory wall']:
        source_is_wall_caster = False
        if 'obj_id' in source:
            for iw_source in map_data['illusory wall'][pos]:
                if 'obj_id' in iw_source:
                    if source['obj_id'] == iw_source['obj_id']:
                        source_is_wall_caster = True
                        break
        if not source_is_wall_caster:
            block_los_into = True
            block_los_beyond = True
            block_los_beyond_1 = True
    
    return block_los_into, block_los_beyond, block_los_beyond_1

def does_tile_block_loe(pos, map_section, map_data, source = {}):
    # block_los_beyond_1 is for walls with narrow openings, like arrow slits
    # can only see into tile adjacent to such a wall
    block_loe_into = False
    block_loe_beyond = False
    block_loe_beyond_1 = False
    tile_type = map_section[pos][0]
    if tile_type == 'wall':
        block_loe_into = True
        block_loe_beyond = True
        block_loe_beyond_1 = True
    elif tile_type == 'wall with large opening':
        block_loe_into = False
        block_loe_beyond = False
        block_loe_beyond_1 = False
    elif tile_type == 'wall with small opening':
        block_loe_into = True
        block_loe_beyond = False
        block_loe_beyond_1 = True
    elif tile_type == 'wall with window':
        block_loe_into = True
        block_loe_beyond = True
        block_loe_beyond_1 = True
    elif tile_type == 'clear wall':
        block_loe_into = True
        block_loe_beyond = True
        block_loe_beyond_1 = True
        
    return block_loe_into, block_loe_beyond, block_loe_beyond_1

def find_los_tiles_in_one_octant(pos, map_section_name, game, radius, o2, source = {}, to_one_tile = False):
    
    # to_one_tile is either False (do all sight lines) or an (x,y) tuple of map pos
    
    # todo - add check for fog, smoke and other things that block los
    # todo - distinguish between and return both line of sight and line of effect
    # todo - determine cover and concealment
    
    map_section = game.map[map_section_name]
    los_tiles = set()
    revealed_tiles = set()  # walls are revealed to be walls, but one doesn't have los into wall tile
    num_source_sight_spots = len(SOURCE_SIGHT_SPOTS)
    num_good_sight_lines = 0
    map_data = game.map_data[map_section_name]
    for source_idx in range(num_source_sight_spots):
        num_slopes = vinfo['slope_numbers'][source_idx]
        if not to_one_tile:
            bits_los = bitarray(num_slopes)
            bits_los.setall(True)
#            bits_small_opening = bitarray(num_slopes)
#            bits_small_opening.setall(False)
        else:
            zot = find_zeroth_octant_tuple(pos, to_one_tile, o2)            
            bits_los = deepcopy(vinfo[zot].four_corner_slopes[source_idx])
        bits_small_opening = bitarray(num_slopes)
        bits_small_opening.setall(False)
        
        viqueue = deque()
        if vinfo[(1,0)].dist <= radius and (pos[0]+vinfo[(1,0)].grid[o2][0], pos[1]+vinfo[(1,0)].grid[o2][1]) in map_section:
            viqueue.append(vinfo[(1,0)])
        if vinfo[(1,1)].dist <= radius and (pos[0]+vinfo[(1,1)].grid[o2][0], pos[1]+vinfo[(1,1)].grid[o2][1]) in map_section:
            viqueue.append(vinfo[(1,1)])
        last = vinfo[(0,0)]
        
        while len(viqueue) > 0:
            vi = viqueue.popleft()
            sightlines_used_to_see_here = bits_los & vi.slope_numbers_sight_into[source_idx]
            if sightlines_used_to_see_here.any():
                last_tile_for_these_sightlines = sightlines_used_to_see_here & bits_small_opening 
                if last_tile_for_these_sightlines.any():
                    bits_los &= ~last_tile_for_these_sightlines
                    bits_small_opening &= ~last_tile_for_these_sightlines
                
                this_xy = ( pos[0] + vi.grid[o2][0], pos[1]+vi.grid[o2][1] )
                revealed_tiles.add(this_xy)
                block_into, block_beyond, block_beyond_1 = does_tile_block_los(this_xy, map_section, map_data, source)
                
                if not block_into:
                    los_tiles.add(this_xy)
                    
                if not block_beyond and block_beyond_1 and vi != vinfo[(1,0)] and vi != vinfo[(1,1)]:
                    bits_small_opening |= vi.slope_numbers_block[source_idx]
                    
                if block_beyond:
                    if (source_idx in INTERNAL_HORIZONTAL_SIGHT_SPOT) and vi.y == 0:
                        horiz_bit = vi.horiz_slope_idx[source_idx]
                        if bits_los[horiz_bit]:
                            adj_pos = (this_xy[0]+vi.adjacent[o2][0], this_xy[1]+vi.adjacent[o2][1])
                            ablock_into, ablock_beyond, ablock_beyond_1 = does_tile_block_los(adj_pos, map_section, map_data, source)
                            if ablock_beyond or ablock_beyond_1:
                                bits_los[horiz_bit] = False  
                            elif vi.next_h.dist <= radius \
                            and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
                            # sighting continues horizontally past the wall...
                                viqueue.append(vi.next_h)
                            
                    if vi.x == vi.y and vi.next_d.dist <= radius and source_idx in INTERNAL_DIAGONAL_SIGHT_SPOT:
                        diag_bit = vi.diag_slope_idx[source_idx]
                        if bits_los[diag_bit] \
                        and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section:
                            viqueue.append(vi.next_d)
                        
                    bits_los &= ~vi.slope_numbers_block[source_idx]
                    
                else:
                    if last != vi.next_h and vi.next_h.dist <= radius \
                    and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
                        last = vi.next_h
                        viqueue.append(vi.next_h)
                    if last != vi.next_d and vi.next_d.dist <= radius \
                    and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section:
                        last = vi.next_d
                        viqueue.append(vi.next_d)
                        
        num_good_sight_lines += bits_los.count()

    return los_tiles, revealed_tiles, num_good_sight_lines

def find_loe_tiles_in_one_octant(pos, map_section_name, game, radius, o2, source = {}, to_one_tile = False):
    
    # to_one_tile is either False (do all sight lines) or an (x,y) tuple of map pos
    
    # todo - add check for fog, smoke and other things that block los
    # todo - distinguish between and return both line of sight and line of effect
    # todo - determine cover and concealment
    
    map_section = game.map[map_section_name]
    loe_tiles = set()
    num_source_sight_spots = len(SOURCE_SIGHT_SPOTS)
    num_good_effect_lines = 0
    map_data = game.map_data[map_section_name]
    for source_idx in range(num_source_sight_spots):
        num_slopes = vinfo['slope_numbers'][source_idx]
        if not to_one_tile:
            bits_loe = bitarray(num_slopes)
            bits_loe.setall(True)
#            bits_small_opening = bitarray(num_slopes)
#            bits_small_opening.setall(False)
        else:
            zot = find_zeroth_octant_tuple(pos, to_one_tile, o2)            
            bits_loe = deepcopy(vinfo[zot].four_corner_slopes[source_idx])
        bits_small_opening = bitarray(num_slopes)
        bits_small_opening.setall(False)
        
        viqueue = deque()
        if vinfo[(1,0)].dist <= radius and (pos[0]+vinfo[(1,0)].grid[o2][0], pos[1]+vinfo[(1,0)].grid[o2][1]) in map_section:
            viqueue.append(vinfo[(1,0)])
        if vinfo[(1,1)].dist <= radius and (pos[0]+vinfo[(1,1)].grid[o2][0], pos[1]+vinfo[(1,1)].grid[o2][1]) in map_section:
            viqueue.append(vinfo[(1,1)])
        last = vinfo[(0,0)]
        
        while len(viqueue) > 0:
            vi = viqueue.popleft()
            sightlines_used_to_see_here = bits_loe & vi.slope_numbers_sight_into[source_idx]
            if sightlines_used_to_see_here.any():
                last_tile_for_these_sightlines = sightlines_used_to_see_here & bits_small_opening 
                if last_tile_for_these_sightlines.any():
                    bits_loe &= ~last_tile_for_these_sightlines
                    bits_small_opening &= ~last_tile_for_these_sightlines
                
                this_xy = ( pos[0] + vi.grid[o2][0], pos[1]+vi.grid[o2][1] )
                block_into, block_beyond, block_beyond_1 = does_tile_block_loe(this_xy, map_section, map_data, source)
                
                if not block_into:
                    loe_tiles.add(this_xy)
                    
                if not block_beyond and block_beyond_1 and vi != vinfo[(1,0)] and vi != vinfo[(1,1)]:
                    bits_small_opening |= vi.slope_numbers_block[source_idx]
                    
                if block_beyond:
                    if (source_idx in INTERNAL_HORIZONTAL_SIGHT_SPOT) and vi.y == 0:
                        horiz_bit = vi.horiz_slope_idx[source_idx]
                        if bits_loe[horiz_bit]:
    #                    if (source_idx in INTERNAL_HORIZONTAL_SIGHT_SPOT) and bits_loe[0] and vi.y == 0:
                            adj_pos = (this_xy[0]+vi.adjacent[o2][0], this_xy[1]+vi.adjacent[o2][1])
                            ablock_into, ablock_beyond, ablock_beyond_1 = does_tile_block_loe(adj_pos, map_section, map_data, source)
                            if ablock_beyond or ablock_beyond_1:
#                                bits_loe[0] = False  
                                bits_loe[horiz_bit] = False  
                            elif vi.next_h.dist <= radius \
                            and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
                            # sighting continues horizontally past the wall...
                                viqueue.append(vi.next_h)
                            
#                    if vi.x == vi.y and vi.next_d.dist <= radius and bits_loe[-1]\
#                    and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section \
#                    and source_idx in INTERNAL_DIAGONAL_SIGHT_SPOT:
                    if vi.x == vi.y and vi.next_d.dist <= radius and source_idx in INTERNAL_DIAGONAL_SIGHT_SPOT:
                        diag_bit = vi.diag_slope_idx[source_idx]
                        if bits_loe[diag_bit] \
                        and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section:
                            viqueue.append(vi.next_d)
                        
                    bits_loe &= ~vi.slope_numbers_block[source_idx]
                    
                else:
                    if last != vi.next_h and vi.next_h.dist <= radius \
                    and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
                        last = vi.next_h
                        viqueue.append(vi.next_h)
                    if last != vi.next_d and vi.next_d.dist <= radius \
                    and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section:
                        last = vi.next_d
                        viqueue.append(vi.next_d)
                        
        num_good_effect_lines += bits_loe.count()

    return loe_tiles, num_good_effect_lines

def creature_here(this_xy, map_data, game):
    creature = None
    for mid in map_data['monsters']:
        mon = game.objectIdDict[mid]
        if mon.pos == this_xy:
            creature = mon
            break
    if not creature:
        for pid in game.charnamesid.itervalues():
            char = game.objectIdDict[mid]
            if char.pos == this_xy:
                creature = char
                break
    return creature

def calc_cover_between_two_tiles(pos, other_pos, map_section_name, game, radius, o2, ranged = True, source = {}):
    # cover levels:
    # 0 none, 1 partial, 2 soft, 3 regular, 4 improved, 5 total
    
    # if ranged = False, then do cover for melee
    
    
    map_section = game.map[map_section_name]
    loe_tiles = set()
    num_source_sight_spots = len(SOURCE_SIGHT_SPOTS)
    unobstructed_effect_lines_list = []
    cover_list = []
    soft_cover_list = []
    map_data = game.map_data[map_section_name]
    zot = find_zeroth_octant_tuple(pos, other_pos, o2)
    tot_effect_lines = 0  
    diag_bit = None          
    for source_idx in range(num_source_sight_spots):
        cover_list.append(0)
        soft_cover_list.append(0)
        num_slopes = vinfo['slope_numbers'][source_idx]
        bits_loe = deepcopy(vinfo[zot].four_corner_slopes[source_idx])
        bits_small_opening = bitarray(num_slopes)
        bits_small_opening.setall(False)
        num_slopes_checking = bits_loe.count()
        
        viqueue = deque()
        if vinfo[(1,0)].dist <= radius and (pos[0]+vinfo[(1,0)].grid[o2][0], pos[1]+vinfo[(1,0)].grid[o2][1]) in map_section:
            viqueue.append(vinfo[(1,0)])
        if vinfo[(1,1)].dist <= radius and (pos[0]+vinfo[(1,1)].grid[o2][0], pos[1]+vinfo[(1,1)].grid[o2][1]) in map_section:
            viqueue.append(vinfo[(1,1)])
        last = vinfo[(0,0)]
        
        while len(viqueue) > 0:
            vi = viqueue.popleft()
            sightlines_used_to_see_here = bits_loe & vi.slope_numbers_sight_into[source_idx]
            if sightlines_used_to_see_here.any():
                last_tile_for_these_sightlines = sightlines_used_to_see_here & bits_small_opening 
                if last_tile_for_these_sightlines.any():
                    bits_loe &= ~last_tile_for_these_sightlines
                    bits_small_opening &= ~last_tile_for_these_sightlines
                    if zot == (vi.x, vi.y):
                        cover_list[source_idx] = max(cover_list[source_idx], 4)
                
                this_xy = ( pos[0] + vi.grid[o2][0], pos[1]+vi.grid[o2][1] )
                block_into, block_beyond, block_beyond_1 = does_tile_block_loe(this_xy, map_section, map_data, source)
                if zot != (vi.x, vi.y):
                    creature = creature_here(this_xy, map_data, game)
                    if creature and not 'incorporeal' in creature.subtype and not creature.is_incorporeal():
                        cover_list[source_idx] = max(cover_list[source_idx], 2)
                        soft_cover_list[source_idx] = max(soft_cover_list[source_idx],1)
                        
                tile_type = map_section[this_xy][0]
                if tile_type == 'low obstacle':
                    dist_obstacle_to_other = sqrt( (other_pos[0]-this_xy[0])**2 + (other_pos[1]-this_xy[1])**2 ) 
                    if dist_obstacle_to_other <= 6:
                        if vi.dist >= dist_obstacle_to_other:
                            cover_list[source_idx] = max(cover_list[source_idx], 3)
                
                if this_xy in findAdjTiles(other_pos[0], other_pos[1], map_section) \
                or (vi != vinfo[(1,0)] and vi != vinfo[(1,1)]):   # targets don't get cover if source is adjacent to wall with opening
                                                                  # (unless target is adjacent)
                    if tile_type == 'wall with large opening':
                        cover_list[source_idx] = max(cover_list[source_idx], 3)
                    
                    if tile_type == 'wall with small opening':
                        cover_list[source_idx] = max(cover_list[source_idx], 4)
                        bits_small_opening |= vi.slope_numbers_block[source_idx]
                
                if not block_into:
                    loe_tiles.add(this_xy)
                    
                if block_beyond:
                    if (source_idx in INTERNAL_HORIZONTAL_SIGHT_SPOT) and vi.y == 0:
                        horiz_bit = vi.horiz_slope_idx[source_idx]
                        if bits_loe[horiz_bit]:
    #                    if (source_idx in INTERNAL_HORIZONTAL_SIGHT_SPOT) and bits_loe[0] and vi.y == 0:
                            adj_pos = (this_xy[0]+vi.adjacent[o2][0], this_xy[1]+vi.adjacent[o2][1])
                            ablock_into, ablock_beyond, ablock_beyond_1 = does_tile_block_loe(adj_pos, map_section, map_data, source)
                            if ablock_beyond or ablock_beyond_1:
                                bits_loe[horiz_bit] = False  
                            elif vi.next_h.dist <= radius \
                            and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
                            # sighting continues horizontally past the wall...
                                viqueue.append(vi.next_h)
                            
#                    if vi.x == vi.y and vi.next_d.dist <= radius and bits_loe[-1]\
#                    and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section \
#                    and source_idx in INTERNAL_DIAGONAL_SIGHT_SPOT:
#                        viqueue.append(vi.next_d)
                    if vi.x == vi.y and vi.next_d.dist <= radius and source_idx in INTERNAL_DIAGONAL_SIGHT_SPOT:
                        diag_bit = vi.diag_slope_idx[source_idx]
                        if bits_loe[diag_bit] \
                        and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section:
                            viqueue.append(vi.next_d)
                        
                    bits_loe &= ~vi.slope_numbers_block[source_idx]
                    
                else:
                    if last != vi.next_h and vi.next_h.dist <= radius \
                    and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
                        last = vi.next_h
                        viqueue.append(vi.next_h)
                    if last != vi.next_d and vi.next_d.dist <= radius \
                    and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section:
                        last = vi.next_d
                        viqueue.append(vi.next_d)

        if source_idx in INTERNAL_DIAGONAL_SIGHT_SPOT:
            if diag_bit != None:
                if bits_loe[diag_bit]:
                    num_slopes_checking += 1
        unobstructed_effect_lines_list.append(bits_loe.count())
        
        if unobstructed_effect_lines_list[source_idx] == 0:
            sight_cover = 5
        elif unobstructed_effect_lines_list[source_idx] <= num_slopes_checking/2:
            sight_cover = 3
        elif unobstructed_effect_lines_list[source_idx] < num_slopes_checking:
            sight_cover = 1
        else:
            sight_cover = 0
            
        cover_list[source_idx] = max(cover_list[source_idx], sight_cover)
        tot_effect_lines += num_slopes_checking
       
        print '########### view utils cover ##############', cover_list[source_idx], sight_cover, unobstructed_effect_lines_list[source_idx], num_slopes_checking, zot, o2 
        
    if ranged:  # in ranged attacks, attacker gets to choose corner with least cover for target
        cover = cover_list[0]
        using_sidx = 0
        for source_idx in range(1,num_source_sight_spots):
            if cover_list[source_idx] < cover:
                cover = cover_list[source_idx]
                using_sidx = source_idx
        soft_cover = soft_cover_list[using_sidx]
    else:
        tot_unobstructed = 0
        for source_idx in range(num_source_sight_spots):
            tot_unobstructed += unobstructed_effect_lines_list[source_idx]
        if tot_unobstructed == 0:
            cover = 5
        elif tot_unobstructed == tot_effect_lines:
            cover = 0
        elif tot_unobstructed <= tot_effect_lines/2:
            cover = 3
        else:
            cover = 1
        # don't see how one could have improved cover for melee, since my arrowslits are an entire 5'x5' wall
        soft_cover = 0
    
    return cover, soft_cover

def find_los_tiles_from_position_within_radius(pos, map_section_name, game, radius = MAX_SIGHT, source = {}):
    los_tiles = set()
    los_tiles.add(pos)
    revealed_tiles = set()
    revealed_tiles.add(pos)
#    vinfo = game.vinfo
    if radius > MAX_SIGHT:
        radius = MAX_SIGHT

    for o2 in range(8):
        
        new_los_tiles, new_revealed_tiles, sight_line_count = find_los_tiles_in_one_octant(pos, map_section_name, game, radius, o2, source)
        los_tiles |= new_los_tiles
        revealed_tiles |= new_revealed_tiles
              
#        for source_idx in range(len(SOURCE_SIGHT_SPOTS)):
#            num_slopes = vinfo['slope_numbers'][source_idx]
#            bits = bitarray(num_slopes)
#            bits.setall(True)
#            viqueue = deque()
#            if vinfo[(1,0)].dist <= radius and (pos[0]+vinfo[(1,0)].grid[o2][0], pos[1]+vinfo[(1,0)].grid[o2][1]) in map_section:
#                viqueue.append(vinfo[(1,0)])
#            if vinfo[(1,1)].dist <= radius and (pos[0]+vinfo[(1,1)].grid[o2][0], pos[1]+vinfo[(1,1)].grid[o2][1]) in map_section:
#                viqueue.append(vinfo[(1,1)])
#            last = vinfo[(0,0)]
#            
#            while len(viqueue) > 0:
#                vi = viqueue.popleft()
#                if (bits & vi.slope_numbers_sight_into[source_idx]).any():
#                    this_xy = ( pos[0] + vi.grid[o2][0], pos[1]+vi.grid[o2][1] )
#                    los_tiles.add(this_xy)
#                    tile_type = map_section[this_xy][0]
#                    if tile_type == 'wall':
#                        if (source_idx in INTERNAL_HORIZONTAL_SIGHT_SPOT) and bits[0] and vi.y == 0:
#                            adjacent_tile_type = map_section[ (this_xy[0]+vi.adjacent[o2][0], this_xy[1]+vi.adjacent[o2][1]) ][0]
#                            if adjacent_tile_type == 'wall':    # only way to block horizontal sight line is for
#                                                                # both adjacent tiles to be wall
#                                bits[0] = False  
#                            elif vi.next_h.dist <= radius \
#                            and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
#                            # sighting continues horizontally past the wall...
#                                viqueue.append(vi.next_h)
#                                
#                        if vi.x == vi.y and vi.next_d.dist <= radius and bits[-1]\
#                        and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section \
#                        and source_idx in INTERNAL_DIAGONAL_SIGHT_SPOT:
#                            viqueue.append(vi.next_d)
#                            
#                        bits &= ~vi.slope_numbers_block[source_idx]
#                    else:
#                        if last != vi.next_h and vi.next_h.dist <= radius \
#                        and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
#                            last = vi.next_h
#                            viqueue.append(vi.next_h)
#                        if last != vi.next_d and vi.next_d.dist <= radius \
#                        and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section:
#                            last = vi.next_d
#                            viqueue.append(vi.next_d)
                            
    return los_tiles, revealed_tiles
	
def find_loe_tiles_from_position_within_radius(pos, map_section_name, game, radius = MAX_SIGHT, source = {}):
    loe_tiles = set()
    loe_tiles.add(pos)
    if radius > MAX_SIGHT:
        radius = MAX_SIGHT

    for o2 in range(8):
        
        new_loe_tiles, sight_line_count = find_loe_tiles_in_one_octant(pos, map_section_name, game, radius, o2, source)
        loe_tiles |= new_loe_tiles
              
    return loe_tiles
    
	
#def find_los_tiles_from_position_within_radius(pos, map_section, game, radius = MAX_SIGHT):
#    los_tiles = set()
#    los_tiles.add(pos)
#    vinfo = game.vinfo
#    if radius > MAX_SIGHT:
#        radius = MAX_SIGHT
#
#    for o2 in range(8):
#        for source_idx in range(len(SOURCE_SIGHT_SPOTS)):
#            num_slopes = vinfo['slope_numbers'][source_idx]
#            bits = bitarray(num_slopes)
#            bits.setall(True)
#            viqueue = deque()
#            if vinfo[(1,0)].dist <= radius and (pos[0]+vinfo[(1,0)].grid[o2][0], pos[1]+vinfo[(1,0)].grid[o2][1]) in map_section:
#                viqueue.append(vinfo[(1,0)])
#            if vinfo[(1,1)].dist <= radius and (pos[0]+vinfo[(1,1)].grid[o2][0], pos[1]+vinfo[(1,1)].grid[o2][1]) in map_section:
#                viqueue.append(vinfo[(1,1)])
#            last = vinfo[(0,0)]
#            
#            while len(viqueue) > 0:
#                vi = viqueue.popleft()
#                if (bits & vi.slope_numbers_sight_into[source_idx]).any():
#                    this_xy = ( pos[0] + vi.grid[o2][0], pos[1]+vi.grid[o2][1] )
#                    los_tiles.add(this_xy)
#                    tile_type = map_section[this_xy][0]
#                    if tile_type == 'wall':
#                        if (source_idx in INTERNAL_HORIZONTAL_SIGHT_SPOT) and bits[0] and vi.y == 0:
#                            adjacent_tile_type = map_section[ (this_xy[0]+vi.adjacent[o2][0], this_xy[1]+vi.adjacent[o2][1]) ][0]
#                            if adjacent_tile_type == 'wall':    # only way to block horizontal sight line is for
#                                                                # both adjacent tiles to be wall
#                                bits[0] = False  
#                            elif vi.next_h.dist <= radius \
#                            and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
#                            # sighting continues horizontally past the wall...
#                                viqueue.append(vi.next_h)
#                                
#                        if vi.x == vi.y and vi.next_d.dist <= radius and bits[-1]\
#                        and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section \
#                        and source_idx in INTERNAL_DIAGONAL_SIGHT_SPOT:
#                            viqueue.append(vi.next_d)
#                            
#                        bits &= ~vi.slope_numbers_block[source_idx]
#                    else:
#                        if last != vi.next_h and vi.next_h.dist <= radius \
#                        and (pos[0]+vi.next_h.grid[o2][0],pos[1]+vi.next_h.grid[o2][1]) in map_section:
#                            last = vi.next_h
#                            viqueue.append(vi.next_h)
#                        if last != vi.next_d and vi.next_d.dist <= radius \
#                        and (pos[0]+vi.next_d.grid[o2][0],pos[1]+vi.next_d.grid[o2][1]) in map_section:
#                            last = vi.next_d
#                            viqueue.append(vi.next_d)
#                            
#    return los_tiles


def find_one_objects_viewed_tiles_within_radius(object, game, radius = MAX_SIGHT):
    
    pos = object.pos
    normal_viewed_tiles = set()
    dim_viewed_tiles = set()
    revealed_tiles = set()
    if pos and not False:       # will be and not blind
        map_section_name = object.map_section
#        map_section = game.map[object.map_section]
        mapsection_lightdata = game.map_data[map_section_name]['light']
#        mapsection_lightdata = game.map_data[object.map_section]['light']
    
        source = {}
        source['obj_id'] = object.id
        if object.vision_type == 'darkvision' and mapsection_lightdata != 'uniform':    
            los_tiles, temp_revealed_tiles = find_los_tiles_from_position_within_radius(pos, map_section_name, game, DARKVISION_RADIUS, source)
            normal_viewed_tiles = los_tiles
            revealed_tiles = temp_revealed_tiles
        los_tiles, temp_revealed_tiles = find_los_tiles_from_position_within_radius(pos, map_section_name, game, radius, source)
        if mapsection_lightdata == 'uniform':
            normal_viewed_tiles = los_tiles
            revealed_tiles = temp_revealed_tiles
    #        for t in los_tiles:
    #            viewed_tiles[t] = 2
        else:
            if object.vision_type == 'normal':
                for t in temp_revealed_tiles:
                    if t in mapsection_lightdata:
                        light_level = mapsection_lightdata[t]
                        if light_level >= DIM_LIGHT_INTENSITY:
                            revealed_tiles.add(t)
                        if t in los_tiles:
                            if light_level >= NORMAL_LIGHT_INTENSITY:
                                normal_viewed_tiles.add(t)
                            elif light_level >= DIM_LIGHT_INTENSITY:
                                dim_viewed_tiles.add(t)
            elif object.vision_type == 'lowlight':
                for t in temp_revealed_tiles:
                    if t in mapsection_lightdata:
                        light_level = mapsection_lightdata[t]
                        if light_level >= ULTRADIM_LIGHT_INTENSITY:
                            revealed_tiles.add(t)
                        if t in los_tiles:
                            if light_level >= DIM_LIGHT_INTENSITY:
                                normal_viewed_tiles.add(t)
                            elif light_level >= ULTRADIM_LIGHT_INTENSITY:
                                dim_viewed_tiles.add(t)
            elif object.vision_type == 'darkvision':
                for t in temp_revealed_tiles:
                    if t in mapsection_lightdata and t not in revealed_tiles:
                        light_level = mapsection_lightdata[t]
                        if light_level >= DIM_LIGHT_INTENSITY:
                            revealed_tiles.add(t)
                        if t in los_tiles:
                            if light_level >= NORMAL_LIGHT_INTENSITY:
                                normal_viewed_tiles.add(t)
                            elif light_level >= DIM_LIGHT_INTENSITY:
                                dim_viewed_tiles.add(t)
                
                    
    #                viewed_tiles.add(t)
    #                viewed_tiles[t] = mapsection_lightdata[t] 
    return normal_viewed_tiles, dim_viewed_tiles, revealed_tiles
    
    
#    viewed_tiles = find_viewed_tiles_from_pos_within_radius(pos, object.map_section, game, radius)
    
#    los_tiles = find_los_tiles_from_position_within_radius(pos, map_section, game, radius)
#    
#    viewed_tiles = {}
#    mapsection_lightdata = game.map_data[object.map_section]['light']
#    if mapsection_lightdata == 'uniform':
#        for t in los_tiles:
#            viewed_tiles[t] = 2
#    else:
#        for t in los_tiles:
#            if t in mapsection_lightdata:
#                viewed_tiles[t] = mapsection_lightdata[t] 
    return viewed_tiles

#def find_viewed_tiles_from_pos_within_radius(pos, map_section_name, game, radius = MAX_SIGHT):
##    map_section = game.map[map_section_name]
#    los_tiles = find_los_tiles_from_position_within_radius(pos, map_section_name, game, radius)
#    viewed_tiles = set()
#    mapsection_lightdata = game.map_data[map_section_name]['light']
#    if mapsection_lightdata == 'uniform':
#        viewed_tiles = los_tiles
##        for t in los_tiles:
##            viewed_tiles[t] = 2
#    else:
#        for t in los_tiles:
#            if t in mapsection_lightdata:
#                viewed_tiles.add(t)
##                viewed_tiles[t] = mapsection_lightdata[t] 
#    return viewed_tiles

def find_light_changes_for_moving_object(object, game, old_pos = None):
    light_level_changes = {}
    map_section_name = object.map_section
    itemslist = object.list_items(listall = True)
    # todo, add variables to mobile_object indicating if and which light
    # source is active, so don't have to search through every item
    for item in itemslist:
        if item.is_showing_light:
            if old_pos:
                light_source = (old_pos,item.bright_light_radius,item.normal_light_radius,item.dim_light_radius,item.ultradim_light_radius)
                old_light_levels = determine_tiles_illuminated_by_lightsource(game, light_source, map_section_name)   
            else:
                old_light_levels = {}         
            if object.pos:
                light_source = (object.pos,item.bright_light_radius,item.normal_light_radius,item.dim_light_radius,item.ultradim_light_radius)
                new_light_levels = determine_tiles_illuminated_by_lightsource(game, light_source, map_section_name)
            else:
                new_light_levels = {}
            
            level_changes = find_tile_level_changes(old_light_levels, new_light_levels)
            apply_tile_level_changes_to_total_levels(level_changes, light_level_changes)
            
    return light_level_changes
    
def find_and_apply_light_and_view_changes_for_moving_object(object, game, old_pos = None):
    light_level_changes = find_light_changes_for_moving_object(object, game, old_pos)
    map_section_name = object.map_section
    apply_tile_level_changes_to_total_levels(light_level_changes, game.map_data[map_section_name]['light'])

    if light_level_changes:
        dict_of_view_info = determine_all_view_levels_for_party(game)
        dict_of_mon_view_info = determine_all_view_levels_for_monsters(game)
        dict_of_view_info.update(dict_of_mon_view_info)
    else:
        dict_of_view_info = {}    
        if object.pos != old_pos:
            normal_viewed_tiles, dim_viewed_tiles, revealed_tiles = find_one_objects_viewed_tiles_within_radius(object, game)
#            object.update_viewed_tiles(normal_viewed_tiles, dim_viewed_tiles)
            dict_of_view_info[object.id] = (normal_viewed_tiles,dim_viewed_tiles,revealed_tiles)
    
#        if object.id in game.charnamesid.values():
#            update_game_best_view_tile_sets(game)   
#            dict_of_all_view_info['party_normal'] = game.tiles_within_party_normal_view     
#            dict_of_all_view_info['party_dim'] = game.tiles_within_party_dim_view
    game.set_objects_viewable_tiles(dict_of_view_info)
    return light_level_changes, dict_of_view_info       

def update_game_best_view_tile_sets_old(game):
    new_set_of_normal_view_tiles = {}
    new_set_of_dim_view_tiles = {}
    for map_section_name in game.map_section_names:
        new_set_of_normal_view_tiles[map_section_name] = set()
        new_set_of_dim_view_tiles[map_section_name] = set()
    for charid in game.charnamesid.itervalues():
        advchar = game.objectIdDict[charid]
        map_section_name = advchar.map_section
        new_set_of_normal_view_tiles[map_section_name] |= advchar.normal_viewed_tiles
        new_set_of_dim_view_tiles[map_section_name] |= advchar.dim_viewed_tiles
    for map_section_name in game.map_section_names:
        new_set_of_dim_view_tiles[map_section_name] -= new_set_of_normal_view_tiles[map_section_name] 
#        newly_viewable_tiles = new_set_of_normal_view_tiles[map_section_name] - game.tiles_within_party_normal_view[map_section_name]
#        newly_dim_viewable_tiles = new_set_of_dim_view_tiles[map_section_name] - game.tiles_within_party_dim_view[map_section_name]
#        newly_viewable_tiles |= newly_dim_viewable_tiles 
#        game.viewlevelChanges[map_section_name] |= newly_viewable_tiles
#        tiles_no_longer_visible = game.tiles_within_party_normal_view[map_section_name] - new_set_of_normal_view_tiles[map_section_name]
#        dim_tiles_no_longer_visible = game.tiles_within_party_dim_view[map_section_name] - new_set_of_dim_view_tiles[map_section_name]
#        tiles_no_longer_visible |= dim_tiles_no_longer_visible 
#        game.viewlevelChanges[map_section_name] |= tiles_no_longer_visible
        game.tiles_within_party_normal_view[map_section_name] = new_set_of_normal_view_tiles[map_section_name]
        game.tiles_within_party_dim_view[map_section_name] = new_set_of_dim_view_tiles[map_section_name]

def update_game_best_view_tile_sets(game, map_section_name):
    new_set_of_normal_view_tiles = set()
    new_set_of_dim_view_tiles = set()
    for charid in game.charnamesid.itervalues():
        advchar = game.objectIdDict[charid]
        if map_section_name == advchar.map_section:
            new_set_of_normal_view_tiles |= advchar.normal_viewed_tiles
            new_set_of_dim_view_tiles |= advchar.dim_viewed_tiles
    new_set_of_dim_view_tiles -= new_set_of_normal_view_tiles 
    game.tiles_within_party_normal_view = new_set_of_normal_view_tiles
    game.tiles_within_party_dim_view = new_set_of_dim_view_tiles
    
#def adjust_view_levels_for_one_object(object, game):
#    viewed_tiles = find_one_objects_viewed_tiles_within_radius(object, game)
#    level_changes = find_tile_level_changes(object.viewed_tiles, viewed_tiles)
#    object.update_viewed_tiles(viewed_tiles)

def determine_all_view_levels_for_party(game):
    dict_of_all_view_info = {}
            
    for charid in game.charnamesid.itervalues():
        advchar = game.objectIdDict[charid]
        normal_viewed_tiles, dim_viewed_tiles, revealed_tiles = find_one_objects_viewed_tiles_within_radius(advchar, game)
#        advchar.update_viewed_tiles(normal_viewed_tiles, dim_viewed_tiles)
        
        dict_of_all_view_info[charid] = (normal_viewed_tiles,dim_viewed_tiles, revealed_tiles)
        
    return dict_of_all_view_info     
            
def determine_all_view_levels_for_monsters(game):
    dict_of_all_view_info = {}

    for section_name in game.map_section_names:
        for mid in game.map_data[section_name]['monsters']:
            mon = game.objectIdDict[mid]
            normal_viewed_tiles, dim_viewed_tiles, revealed_tiles = find_one_objects_viewed_tiles_within_radius(mon, game)
        
            dict_of_all_view_info[mid] = (normal_viewed_tiles,dim_viewed_tiles, revealed_tiles)
        
    return dict_of_all_view_info     
            
def set_all_vis_objects_for_party(game):
    dict_of_vis = {}            
    for charid in game.charnamesid.itervalues():
        enemy_ids, nonmobj_ids = find_all_potentially_vis_objects_for_this_id(charid,game)
        char = game.objectIdDict[charid]
        char.set_all_visible_objects(enemy_ids, nonmobj_ids)        
        dict_of_vis[charid] = (enemy_ids, nonmobj_ids)
    return dict_of_vis
            
def set_all_vis_objects_for_monsters(game):
    dict_of_vis = {}            
    for section_name in game.map_section_names:
        for mid in game.map_data[section_name]['monsters']:
            enemy_ids, nonmobj_ids = find_all_potentially_vis_objects_for_this_id(mid,game)
            mon = game.objectIdDict[mid]
            mon.set_all_visible_objects(enemy_ids, nonmobj_ids)        
            dict_of_vis[mid] = (enemy_ids, nonmobj_ids)
    return dict_of_vis

def find_tile_level_changes(old_levels, new_levels):
    # both old_levels and new_levels are dictionaries
    # with keys as tile xy tuples, and values as level
    # (number) of something
    level_changes = {}
    oldtilelist = old_levels.keys()
    newtilelist = new_levels.keys()
    tiles_now_not_in_new_list = set(oldtilelist) - set(newtilelist)
    for t in tiles_now_not_in_new_list:
        level_changes[t] = -old_levels[t]
    for t in newtilelist:
        if t in oldtilelist:
            change = new_levels[t] - old_levels[t]
            if change != 0:
                level_changes[t] = change
        else:
            level_changes[t] = new_levels[t]
    return level_changes

def apply_tile_level_changes_to_total_levels(level_changes, total_levels):
    # both parameters are dictionaries with tile (x,y) tuples as
    # keys and level changes or levels, respectively, as values
    for t,c in level_changes.iteritems():
        if total_levels != 'uniform':
                
            if t in total_levels:
                total_levels[t] += c
                if total_levels[t] == 0:
                    del total_levels[t]
            else:
                total_levels[t] = c

def remove_tile_level_changes_from_total_levels(level_changes, total_levels):
    # both parameters are dictionaries with tile (x,y) tuples as
    # keys and level changes or levels, respectively, as values
    for t,c in level_changes.iteritems():
        if t in total_levels:
            total_levels[t] -= c
            if total_levels[t] == 0:
                del total_levels[t]
        else:
            total_levels[t] = -c


def find_dict_of_view_set_changes(dict_of_view_info, game):
    dict_of_view_changes = {}
    for id in dict_of_view_info:
        object = game.objectIdDict[id]
        old_normal_set = object.normal_viewed_tiles
        old_dim_set = object.dim_viewed_tiles
        dict_of_view_changes[id] = find_view_set_changes(dict_of_view_info[id], old_normal_set, old_dim_set)
        
    return dict_of_view_changes

def find_view_set_changes(view_info, old_normal_set, old_dim_set):
        new_normal_set = view_info[0]
        new_dim_set = view_info[1]
        new_revealed_set = view_info[2]
        new_normal_view = new_normal_set - old_normal_set
        new_dim_view = new_dim_set - old_dim_set
        removed_normal_view = old_normal_set - new_normal_set
        removed_dim_view = old_dim_set - new_dim_set
        new_revealed_set = new_revealed_set - old_normal_set
        new_revealed_set = new_revealed_set - old_dim_set
        return (new_normal_view, new_dim_view, removed_normal_view, removed_dim_view, new_revealed_set)

def apply_dict_of_view_set_changes_to_total_sets(dict_of_view_changes, game, reverse = False):
    for id in dict_of_view_changes:
        object = game.objectIdDict[id]
        view_changes = dict_of_view_changes[id]
        total_normal_set = object.normal_viewed_tiles
        total_dim_set = object.dim_viewed_tiles
        if reverse:
            reverse_view_set_changes_to_total_sets(view_changes, total_normal_set, total_dim_set)
        else:
            apply_view_set_changes_to_total_sets(view_changes, total_normal_set, total_dim_set)

def apply_view_set_changes_to_total_sets(view_changes, total_normal_set, total_dim_set):
    # positions are (x,y) tuples
    # total_normal_set and total_dim_set are sets of (x,y) tuples
    # view_changes is a tuple with 4 entries:
    # 1st is normal view positions that are to be added to total_normal_set
    # 2nd is dim view positions that are to be added to total_dim_set
    # 3rd is normal view positions that are to be removed from total_normal_set
    # 4th is dim view positions that are to be removed from total_dim_set
    
    total_normal_set |= view_changes[0]
    total_normal_set -= view_changes[2]
    total_dim_set |= view_changes[1]
    total_dim_set -= view_changes[3]
#    total_normal_set = (total_normal_set|view_changes[0]) - view_changes[2]
#    total_dim_set = (total_dim_set|view_changes[1]) - view_changes[3]

def reverse_view_set_changes_to_total_sets(view_changes, total_normal_set, total_dim_set):
    total_normal_set |= view_changes[2]
    total_normal_set -= view_changes[0]
    total_dim_set |= view_changes[3]
    total_dim_set -= view_changes[1]
#    total_normal_set = (total_normal_set|view_changes[2]) - view_changes[0]
#    total_dim_set = (total_dim_set|view_changes[3]) - view_changes[1]

#def add_dict_of_newly_viewed_tiles_to_known_set(dict_of_view_changes, game):
#    for id in dict_of_view_changes:
#        object = game.objectIdDict[id]
#        map_section_name = object.map_section
#        known_set = game.map_data[map_section_name]['known tiles']
#        view_changes = dict_of_view_changes[id]
#        add_newly_viewed_tiles_to_known_set(view_changes, known_set)
#
#def add_newly_viewed_tiles_to_known_set(view_changes, known_set):
#    known_set |= view_changes[0]
#    known_set |= view_changes[1]

    
#def adjust_view(game, viewed_tiles, map_section_name):
#    oldtilelist = game.tilesWithinView.keys()
#    newtilelist = viewed_tiles
#    tilesnowinvis = set(oldtilelist) - set(newtilelist)
#    for t in tilesnowinvis:
#        viewlevel = game.tilesWithinView[t]
#        game.tilesWithinView[t] -= viewlevel
#        if t in game.viewlevelChanges:
#            game.viewlevelChanges[t] -= viewlevel
#        else:
#            game.viewlevelChanges[t] = -viewlevel
#            
#    for t in newtilelist:
#        newviewlevel = game.map_data[map_section_name]['light'][t]
#        if t in game.tilesWithinView:
#            if game.tilesWithinView[t] != newviewlevel:
#                viewchange = newviewlevel - game.tilesWithinView[t] 
#                game.tilesWithinView[t] = newviewlevel
#                if t in game.viewlevelChanges:
#                    game.viewlevelChanges[t] += viewchange
#                else:
#                    game.viewlevelChanges[t] = viewchange
#        else:
#            game.tilesWithinView[t] = newviewlevel
#            game.viewlevelChanges[t] = newviewlevel
  
  
def find_all_light_sources_in_map_section(game, section_name):
    light_source_list = []
    # search characters
    for pcharname in game.chars:
        profile = game.charsplayer[pcharname]
        pcharid = game.charnamesid[pcharname]
        pchar = game.objectIdDict[pcharid]
        if pchar.map_section == section_name:
            itemslist = pchar.list_items(listall = True)
            for item in itemslist:
                if item.is_showing_light:
                    light_source_list.append( (pchar.pos,item.bright_light_radius, item.normal_light_radius, item.dim_light_radius, item.ultradim_light_radius) )
                    
    # search monsters
    
    # search objects on map section
    
    return light_source_list
  
def evaluate_all_light_sources(game):
    map = game.map
    lightdata = {}
    for section_name in game.map_section_names:
        seclightdata = {}
        mapsec_data = game.map_data[section_name]
        if mapsec_data['light'] != 'uniform':
            light_source_list = find_all_light_sources_in_map_section(game, section_name)
            for light_source in light_source_list:
                light_levels = determine_tiles_illuminated_by_lightsource(game, light_source, section_name)
                for tile,llevel in light_levels.iteritems():
                    if tile in seclightdata: 
                        seclightdata[tile] += llevel
                    else:
                        seclightdata[tile] = llevel
            lightdata[section_name] = seclightdata
        else:
            lightdata[section_name] = 'uniform'
            
    return lightdata

def check_for_vis_changes_to_moving_object_old(mo, game):
    total_otherteam_vis = set()
    total_obj_vis = set()
    obj_vis_changes = {}
    map_section_name = mo.map_section
    if mo.objtype == 'playerchar':
        idlist = game.map_data[map_section_name]['monsters']
    elif mo.objtype == 'monster':
        idlist = []
        for id in game.charnamesid.values():
            obj = game.objectIdDict[id]
            if obj.map_section == map_section_name:
                idlist.append(id)
    for id in idlist:
        obj = game.objectIdDict[id]
        if obj.pos in mo.normal_viewed_tiles or obj.pos in mo.dim_viewed_tiles:
            total_otherteam_vis.add(id)
    obj_vis_changes['otherteam_now_vis'] = total_otherteam_vis - mo.visible_otherteam_ids
    obj_vis_changes['otherteam_now_invis'] = mo.visible_otherteam_ids - total_otherteam_vis
    
    for obj_id in game.map_data[map_section_name]['objects']:
        obj = game.objectIdDict[obj_id]
        if obj.pos in mo.normal_viewed_tiles or obj.pos in mo.dim_viewed_tiles:
            total_obj_vis.add(obj_id)
    obj_vis_changes['obj_now_vis'] = total_obj_vis - mo.visible_object_ids
    obj_vis_changes['obj_now_invis'] = mo.visible_object_ids - total_obj_vis
    
    return obj_vis_changes 

def find_all_potentially_vis_objects_for_this_id(thisid,game):
    enemy_ids = set()
    nonmobj_ids = set()
    thisobj = game.objectIdDict[thisid]
#    thisobj.visible_otherteam_ids = set()
#    thisobj.visible_object_ids = set()
    map_section_name = thisobj.map_section
    if thisobj.objtype == 'playerchar':
        idlist = game.map_data[map_section_name]['monsters']
    elif thisobj.objtype == 'monster':
        idlist = []
        for id in game.charnamesid.values():
            obj = game.objectIdDict[id]
            if obj.map_section == map_section_name:
                idlist.append(id)
    for id in idlist:
        obj = game.objectIdDict[id]
        if thisobj.obj_potentially_seeable(obj, game):
#        if obj.pos in thisobj.normal_viewed_tiles \
#        or obj.pos in thisobj.dim_viewed_tiles:
            enemy_ids.add(id)
#            thisobj.visible_otherteam_ids.add(id)

    for obj_id in game.map_data[map_section_name]['objects']:
        obj = game.objectIdDict[obj_id]
        if thisobj.obj_potentially_seeable(obj, game):
#        if obj.pos in thisobj.normal_viewed_tiles \
#        or obj.pos in thisobj.dim_viewed_tiles:
            nonmobj_ids.add(obj_id)
#            thisobj.visible_object_ids.add(obj_id)
    
    return enemy_ids, nonmobj_ids

def find_other_ids_potential_sight_of_this_id(this_id, game):
#    nonmover_gaining_vis = set()
#    nonmover_losing_vis = set()
    potential_viewers = set()
    non_viewers = set()
    this_obj = game.objectIdDict[this_id]
    map_section_name = this_obj.map_section
    
    if this_obj.objtype == 'playerchar':
        idlist = game.map_data[map_section_name]['monsters']
    elif this_obj.objtype == 'monster':
        idlist = []
        for id in game.charnamesid.values():
            obj = game.objectIdDict[id]
            if obj.map_section == map_section_name:
                idlist.append(id)
    else:
        # this_obj is some non-moving object
        idlist = []
        idlist.extend(game.map_data[map_section_name]['monsters'])
        idlist.extend(game.charnamesid.values())
            
    for id in idlist:
        obj = game.objectIdDict[id]
        if obj.obj_potentially_seeable(this_obj, game):
            potential_viewers.add(id)
        else:
            non_viewers.add(id)
    
    return potential_viewers, non_viewers


#def check_for_and_apply_vis_changes_of_nonmoving_object(mo, game):
#    nonmover_gaining_vis = set()
#    nonmover_losing_vis = set()
#    map_section_name = mo.map_section
#    
#    if mo.objtype == 'playerchar':
#        idlist = game.map_data[map_section_name]['monsters']
#        otype = 'mobj'
#    elif mo.objtype == 'monster':
#        idlist = []
#        for id in game.charnamesid.values():
#            obj = game.objectIdDict[id]
#            if obj.map_section == map_section_name:
#                idlist.append(id)
#        otype = 'mobj'
#    else:
#        # mo is some non-moving object
#        idlist = []
#        idlist.extend(game.map_data[map_section_name]['monsters'])
#        idlist.extend(game.charnamesid.values())
#        otype = 'nonmobj'
#            
#    if otype == 'mobj':
#        for id in idlist:
#            obj = game.objectIdDict[id]
#            if mo.id not in obj.visible_otherteam_ids \
#            and (mo.pos in obj.normal_viewed_tiles \
#            or mo.pos in obj.dim_viewed_tiles):
#                nonmover_gaining_vis.add(id)
#                obj.apply_vis_changes(otherteam_now_vis = set([mo.id]))
#            
#            if mo.id in obj.visible_otherteam_ids \
#            and mo.pos not in obj.normal_viewed_tiles \
#            and mo.pos not in obj.dim_viewed_tiles:
#                nonmover_losing_vis.add(id)
#                obj.apply_vis_changes(otherteam_now_invis = set([mo.id]))
#    elif otype == 'nonmobj':
#        for id in idlist:
#            obj = game.objectIdDict[id]
#            if mo.id not in obj.visible_object_ids \
#            and (mo.pos in obj.normal_viewed_tiles \
#            or mo.pos in obj.dim_viewed_tiles):
#                nonmover_gaining_vis.add(id)
#                obj.apply_vis_changes(obj_now_vis = set([mo.id]))
#            
#            if mo.id in obj.visible_object_ids \
#            and mo.pos not in obj.normal_viewed_tiles \
#            and mo.pos not in obj.dim_viewed_tiles:
#                nonmover_losing_vis.add(id)
#                obj.apply_vis_changes(obj_now_invis = set([mo.id]))
#    
#    return (nonmover_gaining_vis, nonmover_losing_vis)

    
def apply_others_vis_changes_of_mobj_id(moving_id, sight_changes, game):
    for nonmoving_id in sight_changes[0]:
        obj = game.objectIdDict[nonmoving_id]
        obj.apply_vis_changes(otherteam_now_vis = set([moving_id]))
    for nonmoving_id in sight_changes[1]:
        obj = game.objectIdDict[nonmoving_id]
        if moving_id in obj.visible_otherteam_ids:
            obj.apply_vis_changes(otherteam_now_invis = set([moving_id]))
    
def reverse_others_vis_changes_of_mobj_id(moving_id, sight_changes, game):
    for nonmoving_id in sight_changes[0]:
        obj = game.objectIdDict[nonmoving_id]
        if moving_id in obj.visible_otherteam_ids:
            obj.apply_vis_changes(otherteam_now_invis = set([moving_id]))
    for nonmoving_id in sight_changes[1]:
        obj = game.objectIdDict[nonmoving_id]
        obj.apply_vis_changes(otherteam_now_vis = set([moving_id]))
    
def apply_others_vis_changes_of_nonmobj_id(id, sight_changes, game):
    for other_id in sight_changes[0]:
        obj = game.objectIdDict[other_id]
        obj.apply_vis_changes(obj_now_vis = set([id]))
    for other_id in sight_changes[1]:
        obj = game.objectIdDict[other_id]
        if id in obj.visible_object_ids:
            obj.apply_vis_changes(obj_now_invis = set([id]))
    
def reverse_others_vis_changes_of_nonmobj_id(id, sight_changes, game):
    for other_id in sight_changes[0]:
        obj = game.objectIdDict[other_id]
        if id in obj.visible_object_ids:
            obj.apply_vis_changes(obj_now_invis = set([id]))
    for other_id in sight_changes[1]:
        obj = game.objectIdDict[other_id]
        obj.apply_vis_changes(obj_now_vis = set([id]))
    
def find_mobj_ids_that_see_this_id(thisid, game):
    lostobj = game.objectIdDict[thisid]
    map_section_name = lostobj.map_section
    ids_that_see = set()
    
    if lostobj.objtype == 'playerchar':
        idlist = game.map_data[map_section_name]['monsters']
        otype = 'mobj'
    elif lostobj.objtype == 'monster':
        idlist = []
        for id in game.charnamesid.values():
            obj = game.objectIdDict[id]
            if obj.map_section == map_section_name:
                idlist.append(id)
        otype = 'mobj'
    else:
        # thisid is some non-moving object
        idlist = []
        idlist.extend(game.map_data[map_section_name]['monsters'])
        idlist.extend(game.charnamesid.values())
        otype = 'nonmobj'
            
    if otype == 'mobj':
        for id in idlist:
            if id != thisid:
                obj = game.objectIdDict[id]
                if thisid in obj.visible_otherteam_ids:
                    ids_that_see.add(id)
#                    obj.visible_otherteam_ids.remove(thisid)

    elif otype == 'nonmobj':
        for id in idlist:
            if id != thisid:
                obj = game.objectIdDict[id]
                if thisid in obj.visible_object_ids:
                    ids_that_see.add(id)
#                    obj.visible_object_ids.remove(thisid)
    return ids_that_see
        
    
def remove_id_from_other_vis_lists(lostid, ids_that_see, game):
    lostobj = game.objectIdDict[lostid]
    if lostobj.objtype == 'playerchar':
        otype = 'mobj'
    elif lostobj.objtype == 'monster':
        otype = 'mobj'
    else:
        otype = 'nonmobj'
    if otype == 'mobj':
        for id in ids_that_see:
            obj = game.objectIdDict[id]
            obj.apply_vis_changes(otherteam_now_invis = set([lostid]))
    elif otype == 'nonmobj':
        for id in ids_that_see:
            obj = game.objectIdDict[id]
            obj.apply_vis_changes(obj_now_invis = set([lostid]))
        
def add_id_to_other_vis_lists(newid, ids_that_see, game):
    newobj = game.objectIdDict[newid]
    if newobj.objtype == 'playerchar':
        otype = 'mobj'
    elif newobj.objtype == 'monster':
        otype = 'mobj'
    else:
        otype = 'nonmobj'
    if otype == 'mobj':
        for id in ids_that_see:
            obj = game.objectIdDict[id]
            obj.apply_vis_changes(otherteam_now_vis = set([newid]))
    elif otype == 'nonmobj':
        for id in ids_that_see:
            obj = game.objectIdDict[id]
            obj.apply_vis_changes(obj_now_vis = set([newid]))
        

#def adjustViewLevels(object,game,loseallvis = False, forceadjust = False):
#    
#        # need view levels for each nation
#    
#        if forceadjust or object.team == game.myteam:
#            n = object.nation
#            mn = game.mynation        
#
#            oldtilelist = object.absoluteTilesWithinViewForThisUnit.keys()
#            if loseallvis:
#                newtilelist = []
#            else:
#                newtilelist = absolutePosPlusRelativeTilelist(object.relativeTilesWithinView,object.pos,game)
#            
#            # find tiles no longer in newtilelist
#            tilesnowinvis = set(oldtilelist) - set(newtilelist)
#
#            for t in tilesnowinvis:
#                viewlevel = object.absoluteTilesWithinViewForThisUnit[t]
#                if n == mn:
#                    if t in game.viewlevelChanges: 
#                        game.viewlevelChanges[t] -= viewlevel
#                    else:
#                        game.viewlevelChanges[t] = -viewlevel
#
#                    game.tilesWithinView[t] -= viewlevel
#                    
#                del object.absoluteTilesWithinViewForThisUnit[t]
#                
#                    
#            for t in newtilelist:
#                newviewlevel = object.viewlevel * object.searching   
#                    # can put function that depends on t and unit pos in here
#                if t not in object.absoluteTilesWithinViewForThisUnit:
#                    object.absoluteTilesWithinViewForThisUnit[t] = newviewlevel
#                    if n == mn:
#                        if t in game.viewlevelChanges: 
#                            game.viewlevelChanges[t] += newviewlevel
#                        else:
#                            game.viewlevelChanges[t] = newviewlevel
#                        
#                        if t in game.tilesWithinView:       # from some other unit
#                            game.tilesWithinView[t] += newviewlevel
#                        else:
#                            game.tilesWithinView[t] = newviewlevel
#                    
#                elif object.absoluteTilesWithinViewForThisUnit[t] != newviewlevel:
#                    oldviewlevel = object.absoluteTilesWithinViewForThisUnit[t]
#                    object.absoluteTilesWithinViewForThisUnit[t] = newviewlevel
#                    if n == mn:
#                        viewlevelchange = newviewlevel - oldviewlevel
#                        if t in game.viewlevelChanges: 
#                            game.viewlevelChanges[t] += viewlevelchange
#                        else:
#                            game.viewlevelChanges[t] = viewlevelchange
#                        game.tilesWithinView[t] += viewlevelchange
#                        
#    
#                            
                    
                        
                        
                        
                    
                
                
