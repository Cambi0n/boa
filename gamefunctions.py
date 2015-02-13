from math import *
#from random import *

#from numpy import *

#import pygame
#from pygame.locals import *
import random
from time import clock

from events import *
from evmanager import *
from game import *
from userconstants import *
#import view_utils

def HexColor(rgb, alphatoo = False):

    if alphatoo:
        return hex(rgb[0]*256*256*256 + rgb[1]*256*256 + rgb[2]*256 + rgb[3])
    else:
        return hex(rgb[0]*256*256 + rgb[1]*256 + rgb[2])


#------------------------------------------------------------------------------
# not used atm, but keeping it around.  might be useful for determining if combat
def FindEnemyUnitsInRange(unit, range, game):
    """..."""

    unitposx = unit.pos[0]
    unitposy = unit.pos[1]
    thisteam = unit.team

    eUnitsInRange = []

    for n in game.Nations:
        if thisteam != game.Nations[n].team:
            eN = game.Nations[n]
            eUnitList = eN.units
            for eu in eUnitList:
                dist = sqrt((eu.pos[0]-unitposx)**2 + (eu.pos[1]-unitposy)**2)
                if dist <= range:
                    eUnitsInRange.append(eu)

    return(eUnitsInRange)


#------------------------------------------------------------------------------
def FindUnitFromUID(unid, game):
    foundunit = None
    for n in game.nations:
        unitlist = game.Nations[n].units
        for u in unitlist:
            if u.uid == unid:
                foundunit = u
                return foundunit
    if foundunit == None:
        print 'Error, no unit with ' + str(unid) + ' exists'

def FindPath(startpos, endpos, nextsqonly = False):
    sqpath = []
    curx = startpos[0]
    cury = startpos[1]
    
    while (curx,cury) != endpos:
        curangle = atan2( endpos[1] - cury, endpos[0] - curx )
        if curangle < 3*pi/8 and curangle > -3*pi/8:
            curx += 1
            if curangle > pi/8:
                cury += 1
            elif curangle < -pi/8:
                cury -= 1
        elif curangle > 3*pi/8:
            if curangle < 7*pi/8:
                cury += 1
                if curangle > 5*pi/8:
                    curx -= 1
            else:
                curx -= 1
        else:
            if curangle > -7*pi/8:
                cury -= 1
                if curangle < -5*pi/8:
                    curx -= 1
            else:
                curx -= 1
                
        sqpath.append( (curx,cury) )
        
        if nextsqonly:
            break
        
    return sqpath

class asTile:
    def __init__(self, xy):
        self.xy = xy
        self.g = 0
        self.h = 0
        self.f = 0
        self.parent = None
        
def diagDist(sx, sy, gx, gy):
    
    h_diagonal = min(abs(sx-gx), abs(sy-gy))
    h_straight = (abs(sx-gx) + abs(sy-gy))
    if wrap_East_West or wrap_North_South:
        left = min(sx,gx)
        right = max(sx,gx)
        top = min(sy,gy)
        bottom = max(sy,gy)
        if wrap_East_West:
            left = left + mapdim[0]
        if wrap_North_South:
            top = top + mapdim[1]
            
        hdiag2 = min(abs(left-right), abs(top-bottom))
        hstraight2 = (abs(left-right) + abs(top-bottom))
        
        h_diagonal = min(h_diagonal,hdiag2)
        h_straight = min(h_straight,hstraight2)
            
    return 1.414 * h_diagonal + (h_straight - 2*h_diagonal)

adjmatrix = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]

def findAdjTiles(x,y, mapsec):
    adj = []
    
#    mapsec = game.map[object.map_section]
    
    xmax = mapsec['dim'][0]-1
    ymax = mapsec['dim'][1]-1
    
    for (xp,yp) in adjmatrix:
        xt = x + xp
        if xt < 0:
            if wrap_East_West:
                xn = xmax
            else:
                continue
        elif xt > xmax:
            if wrap_East_West:
                xn = 0
            else:
                continue
        else:
            xn = xt
            
        yt = y + yp
        if yt < 0:
            if wrap_North_South:
                yn = ymax
            else:
                continue
        elif yt > ymax:
            if wrap_North_South:
                yn = 0
            else:
                continue
        else:
            yn = yt
            
        adj.append( (xn,yn) )
        
    return adj


def current_energy_should_be_wiped(mo):
    wipe = True
    if mo.orders and mo.current_energy_ord:
        ord = mo.orders[0]
        if ord[0] == 'move':
            nextsq = ord[1][0]
            if nextsq == mo.current_energy_ord[1][0]:
                wipe = False
                
    return wipe  

#def find_time_to_next_move_old(game,mo,next_sq):
#    # returns the time to go from mo.pos to next_sq
#    map_section = game.map[mo.map_section]
##    terrain = game.map[mo.map_section][next_sq][0]    
#    stealth_mode = mo.findCurrentMode('stealth', game)
#    searching_mode = mo.findCurrentMode('searching', game)
#    
#    phased_cost = cost_to_adjacent(mo.pos, next_sq, mo, map_section, stealth_mode, searching_mode)
#    if game.move_mode == 'phased':
#        mode_speed_adjust = 1.0
#        mode_time_adjust = 1.0
#    else:
#        mode_speed_adjust = free_move_to_phased_move_speed_fraction
#        mode_time_adjust = game.free_move_mode_time_factor
#    this_speed = 2. * mo.movespeed * mode_speed_adjust / (seconds_per_round * phased_cost)    # in squares per second
#                # the factor of 2 is because move speeds are given in squares per movement action, but
#                # seconds_per_round is for the full round (move + standard action)
#    time_required = mode_time_adjust / this_speed    # in seconds
#    
#    return time_required

def find_final_path_idx_within_time(game, mo, path, max_time, current_pos = None):
    total_time = 0.
    if not current_pos:
        current_pos = mo.pos
    if path:
        for idx,next_sq in enumerate(path):
            total_time += find_time_to_next_move(game, mo, next_sq, current_pos )
            return_idx = idx
            if total_time > max_time:
                if idx == 0:
                    return_idx = None
                else:
                    return_idx = idx - 1
                break
            current_pos = next_sq
    else: 
        return_idx = None
    return return_idx

def find_time_to_next_move(game,mo,next_sq, oldpos = None):
    # returns the time to go from mo.pos to next_sq
    if not oldpos:
        oldpos = mo.pos
    map_section = game.map[mo.map_section]
    
    if game.move_mode == 'phased':
        mode_speed_adjust = 1.0
    else:
        mode_speed_adjust = free_move_to_phased_move_speed_fraction
        
    movespeed = mo.find_movespeed(game)        
    phased_cost = cost_to_adjacent(oldpos, next_sq, mo, map_section)
#    this_speed = 2. * mo.movespeed * free_move_to_phased_move_speed_fraction / (seconds_per_round * phased_cost)    # in squares per second
                # the factor of 2 is because move speeds are given in squares per movement action, but
                # seconds_per_round is for the full round (move + standard action)
    time_required = int(round(seconds_per_round * 1000. * phased_cost) / (2. * movespeed * mode_speed_adjust))    # in ms
                # the factor of 2 is because move speeds are given in squares per movement action, but
                # seconds_per_round is for the full round (move + standard action)
    
    return time_required

def determine_casting_time(game,obj,spell_name):
    spell = game.complete_dict_of_spells[spell_name]
    casting_time = spell.casting_time
    time_required = 10
    if casting_time == 'standard':
        time_required = return_standard_action_time()
    return time_required

def return_standard_action_time():
    return int(round(seconds_per_round * 1000. * num_pulses_for_standard_action / num_pulses_per_unit))
    
def return_move_action_time():
    return int(round(seconds_per_round * 1000. * num_pulses_for_move_action / num_pulses_per_unit))
    
#def find_pulse_for_next_move(game,mo):
#    print 'gamefunc, next move pulse', mo.orders
#    next_sq = mo.orders[0][1][0]
#    if mo.pos[0] != next_sq[0] and mo.pos[1] != next_sq[1]:  # move is diagonal
#        distance_factor = 1.414
#    else:
#        distance_factor = 1.0
#    terrain = game.map[mo.map_section][next_sq][0]    
#    move_cost = distance_factor * calc_move_cost(mo, terrain)
#    if mo.action_mode == 'move':
#        total_pulses = num_pulses_for_move_action
#    else:
#        total_pulses = num_pulses_for_standard_action
#    exact_pulses_to_get_there = total_pulses * move_cost/mo.movespeed + mo.residual_move_pulses 
#    int_pulses_to_get_there = int(round(exact_pulses_to_get_there))
#    residual = exact_pulses_to_get_there - int_pulses_to_get_there
#    mo.set_residual_move_pulses(residual)
#    return int_pulses_to_get_there
#            
#    
#def find_pulse_for_next_action(game,id,current_pulse):
#    mo = game.objectIdDict[id]
#    next_pulse = -1
#    if mo.orders:
#        ord = mo.orders[0]
#        if ord[0] == 'move':
#            next_pulse = current_pulse + find_pulse_for_next_move(game,mo)
#        elif ord[0] == 'standard_attack':
#            next_pulse = current_pulse + int(num_pulses_per_unit/2)
#        elif ord[0] == 'cast_spell':
#            next_pulse = current_pulse + int(num_pulses_per_unit/2)
#            
#    return next_pulse 
    
#def find_time_for_next_action(game,id):
#    mo = game.objectIdDict[id]
#    next_pulse = -1
#    if mo.orders:
#        ord = mo.orders[0]
#        if ord[0] == 'move':
#            next_pulse = current_pulse + find_time_to_next_move(game,mo)
#        elif ord[0] == 'standard_attack':
#            next_pulse = current_pulse + int(num_pulses_per_unit/2)
#        elif ord[0] == 'cast_spell':
#            next_pulse = current_pulse + int(num_pulses_per_unit/2)
#            
#    return next_pulse 
    
def aStar(start, end, object, game, mapsection, adjacent_costs = None, move_adjacent = False): 
    
    if start == end:
        return [], 0.
    
    openList = set() 
    closedList = set() 
    
    tiledict = {}
 
    def retracePath(c): 
        path = [c.xy] 
        totalcost = c.g
        while c.parent is not None: 
            c = c.parent 
            path.append(c.xy) 
        path.reverse()
        path.pop(0) 
        return path, totalcost 


    starttile = asTile(start)
    tiledict[start] = starttile
    endtile = asTile(end)
    tiledict[end] = endtile
    #movespeed = calcObjectMovespeed(object, game, stealthmode, searchmode, None, False)
    
    currenttile = starttile
 
    openList.add(starttile)    # [(startx, starty), h val, (parentx, parenty)]  
    while openList: 
        currenttile = sorted(openList, key=lambda inst:inst.f)[0]
        if not move_adjacent: 
            if currenttile == endtile: 
                return retracePath(currenttile) 
        openList.remove(currenttile) 
        closedList.add(currenttile) 
        adj = findAdjTiles(currenttile.xy[0],currenttile.xy[1], game.map[object.map_section])
        if move_adjacent:
#            print 'aStar1', endtile.xy, currenttile.xy, adj
            if endtile.xy in adj:
                return retracePath(currenttile)
        for xytuple in adj:
            if xytuple not in tiledict:
                tile = asTile(xytuple)
                tiledict[xytuple] = tile
            else:
                tile = tiledict[xytuple] 
            if tile not in closedList:
                ''' 
                if adjacent_costs and (currenttile.xy, tile.xy) in adjacent_costs:
                    adj_cost = adjacent_costs[(currenttile.xy, tile.xy)]
                else:
                    adj_cost = cost_to_adjacent(currenttile.xy, tile.xy, object, game.map[mapsection], stealthmode, searchmode)
                '''
                adj_cost = cost_to_adjacent(currenttile.xy, tile.xy, object, game.map[mapsection])
                tentative_g = currenttile.g + adj_cost
                #tentative_g = currenttile.g + timeToAdj(currenttile.xy, tile.xy, object, game, stealthmode, searchmode, mapsection)
                
                if tile not in openList:
                    openList.add(tile)
                    tentative_is_better = True
                elif tentative_g < tile.g:
                    tentative_is_better = True
                else:
                    tentative_is_better = False
                    
                if tentative_is_better:
                    tile.parent = currenttile
                    tile.g = tentative_g
                    #tile.h = diagDist(tile.xy[0], tile.xy[1], endtile.xy[0], endtile.xy[1]) / movespeed 
                    tile.h = diagDist(tile.xy[0], tile.xy[1], endtile.xy[0], endtile.xy[1]) 
                    tile.f = tile.g + tile.h

#    print 'aStar2'
    return [],0 


def aStar_track_possibles(start, end, object, game, mapsection, move_points_left, adjacent_costs = None): 
    
    if start == end:
        return set()
    
    openList = set() 
    closedList = set() 
    new_possible_locs = set()
    
    tiledict = {}
 

    starttile = asTile(start)
    tiledict[start] = starttile
    endtile = asTile(end)
    tiledict[end] = endtile
    #movespeed = calcObjectMovespeed(object, game, stealthmode, searchmode, None, False)
    
    currenttile = starttile
 
    openList.add(starttile)    # [(startx, starty), h val, (parentx, parenty)]  
    while openList: 
        currenttile = sorted(openList, key=lambda inst:inst.f)[0] 
        if currenttile == endtile: 
#            return retracePath(currenttile) 
            return new_possible_locs 
        openList.remove(currenttile) 
        closedList.add(currenttile) 
        #todo - optimize next line so walls aren't included?
        adj = findAdjTiles(currenttile.xy[0],currenttile.xy[1], game.map[object.map_section])
        for xytuple in adj:
            if xytuple not in tiledict:
                #todo - create all the tiles once and pass it in, since I'll be
                # using them all anyways?  that way won't have to create same tile
                # multiple times.
                tile = asTile(xytuple)
                tiledict[xytuple] = tile
            else:
                tile = tiledict[xytuple] 
            if tile not in closedList:
                 
                if adjacent_costs and (currenttile.xy, tile.xy) in adjacent_costs:
                    adj_cost = adjacent_costs[(currenttile.xy, tile.xy)]
                else:
                    adj_cost = cost_to_adjacent(currenttile.xy, tile.xy, object, game.map[mapsection])
                
#                adj_cost = cost_to_adjacent(currenttile.xy, tile.xy, object, game.map[mapsection], stealthmode, searchmode)
                tentative_g = currenttile.g + adj_cost
                #tentative_g = currenttile.g + timeToAdj(currenttile.xy, tile.xy, object, game, stealthmode, searchmode, mapsection)
                
                if tile not in openList:
                    openList.add(tile)
                    tentative_is_better = True
                elif tentative_g < tile.g:
                    tentative_is_better = True
                else:
                    tentative_is_better = False
                    
                if tentative_is_better:
                    if tentative_g <= move_points_left:
                        new_possible_locs.add(tile.xy)
                    tile.g = tentative_g
                    #tile.h = diagDist(tile.xy[0], tile.xy[1], endtile.xy[0], endtile.xy[1]) / movespeed 
                    tile.h = diagDist(tile.xy[0], tile.xy[1], endtile.xy[0], endtile.xy[1]) 
                    tile.f = tile.g + tile.h
                    
    return set() 

def find_allowed_moves(start, object, move_points_left, game):
    starttime = clock()
#    allowed_moves = []
#    movespeed = calcObjectMovespeed(object, game, stealthmode, searchmode, None, False)
    relative_tiles = relativeTilesWithinRadius(move_points_left)
    map_section_name = object.map_section
    map_section = game.map[map_section_name]
    abs_xy_list = absolutePosPlusRelativeTilelist(relative_tiles, start, map_section)
    nonwall_xy_list = eliminate_wall_xy_positions(abs_xy_list, map_section)
    
    #compile list of all allowed adjacent movement costs within nonwall_xy_list
    
    adjacent_costs = {}
    for xy_start in nonwall_xy_list:
        adj_xy_list = find_adjacent_xypos_within_list(xy_start, nonwall_xy_list)
        for xy_end in adj_xy_list:
            cost = cost_to_adjacent(xy_start, xy_end, object, map_section)
            adjacent_costs[(xy_start,xy_end)] = cost
             
    found_possible = set()   
    for xy_end in nonwall_xy_list:
        if xy_end in found_possible:
            continue
        else:
    #        path, tcost = aStar(start, xy_end, object, game, stealthmode, searchmode, map_section_name, adjacent_costs)
#            path, tcost = aStar(start, xy_end, object, game, stealthmode, searchmode, map_section_name)
            new_found_possible = aStar_track_possibles(start, xy_end, object, game, map_section_name, move_points_left, adjacent_costs)
            found_possible = found_possible.union(new_found_possible)
#            if tcost < move_points_left:
#                allowed_moves.append(xy_end)
    
    occupied_positions = set()
    if object.objtype == 'monster':
        for id in game.charnamesid.values():
            char = game.objectIdDict[id]
            occupied_positions.add(char.pos)
    elif object.objtype == 'playerchar':
        for id in game.map_data[map_section_name]['monsters']:
            mon = game.objectIdDict[id]
            occupied_positions.add(mon.pos)
            
    found_possible -= occupied_positions
       
    elapsed = clock()-starttime
    print 'elapsed', elapsed
#    return allowed_moves
    return found_possible
            
            
def cost_to_adjacent(sxy, fxy, object, map_section):
    '''
    This routine is used in 2 ways.  First, when the host executes orders, so
    the current modes of the object is used.
    Second, when calculating order times, so the modes of the object at a particular 
    point in the order cycle are needed.
    '''
    
    if sxy[0] != fxy[0] and sxy[1] != fxy[1]:  # move is diagonal
        if map_section[(sxy[0],fxy[1])][0] == 'wall' or map_section[(fxy[0],sxy[1])][0] == 'wall':
            # diagonal moves through a wall corner are not allowed
            distfactor = 10000
        else:  
            distfactor = 1.414
    else:
        distfactor = 1.0
        
    terrain = map_section[fxy][0]    
    cost_modifier = calc_move_cost(object, terrain)    

    cost = cost_modifier * distfactor
    return cost        


def eliminate_wall_xy_positions(init_xylist, map_section):
    final_xylist = []
    for xy in init_xylist:
        if map_section[xy][0] != 'wall':
            final_xylist.append(xy)
    return final_xylist
                    
def find_adjacent_xypos_within_list(xy, xylist):
    adj = []
    
    for (xp,yp) in adjmatrix:
        xt = xy[0] + xp
        yt = xy[1] + yp
        if (xt,yt) in xylist:
            adj.append( (xt,yt) )
        
    return adj

def relativeTilesWithinRadius(radius):
    tilelist = []
    radius = int(round(radius))
    if radius < 0:
        radius = 0
    for x in range(-radius,radius+1):
        for y in range(-radius,radius+1):
            if int(round(sqrt(x**2 + y**2))) <= radius:
                tilelist.append((x,y))
    return tilelist

def absolutePosPlusRelativeTilelist(tilelist,pos,map_section):
    xpos = pos[0]
    ypos = pos[1]
    xmax = map_section['dim'][0]-1
    ymax = map_section['dim'][1]-1
    #xmax = game.mapdim[0]-1
    #ymax = game.mapdim[1]-1
    absxylist = []
    for (xp,yp) in tilelist:
        skip = False
        x1 = xpos+xp
        if x1 < 0:
            skip = True
        elif x1 > xmax:
            skip = True
        
        y1 = ypos + yp
        if y1 < 0:
            skip = True
        elif y1 > ymax:
            skip = True
            
        if not skip:
            absxylist.append( (x1,y1) )
        
    return absxylist    

    
#def calcObjectMovespeed(object, game, terrain = None, doCombatEffects = True):
#    ''' stealthmode and search mode are either single values if object
#    is a single unit, or are lists if object is a group.  If lists, then one value
#    per member of group.
#    '''
#    
#    if object.objtype == 'playerchar' or object.objtype == 'monster':
#        return calcUnitMovespeed(object, terrain, doCombatEffects)
#    elif object.objtype == 'movementgroup':
#        idx = 0
#        firstunit = game.objectIdDict[object.allmembers[idx]]
#        minspeed = calcUnitMovespeed(firstunit, terrain, doCombatEffects)
#        for uid in object.members[1:]:
#            idx += 1
#            u = game.objectIdDict[uid]
#            testspeed = calcUnitMovespeed(u, terrain, doCombatEffects)
#            if testspeed < minspeed:
#                minspeed = testspeed
#        return minspeed
#        
        
#def calcUnitMovespeed(unit, terrain = None, doCombatEffects = False):
#    if terrain:
#        terrainmod = TerrainMovementFactor[terrain]
#    else:
#        terrainmod = 1.0
#    movespeed = unit.movespeed * terrainmod
#    if doCombatEffects:
#        pass
##        todo: check for enemy zone of control
##        if unit.beingAttackedBy:
##            movespeed = movespeed * PinnedMovementMultiplier
#            
#    return movespeed

def calc_move_cost(object, terrain = None):
    # todo - should make terrain movement costs (and maybe also 
    # movement penalties/benefits for stealth/searching) specific to object
    # e.g., some monsters or races might be able to move faster on ice
    # than others
    
    if terrain:
        terrainmod = TerrainMovementFactor[terrain]
    else:
        terrainmod = 1.0
    move_cost = terrainmod
    return float(move_cost)
        
#def parse_damage(damage):
#    
#    parsed_damage_list = []
#
#    if hasattr(damage, '__iter__'):
#        for dstr1 in damage:
#            parsed_damage_list.append(parse_damage_string(dstr1))
#    else:
#        parsed_damage_list.append(parse_damage_string(damage))
#    return parsed_damage_list
        
def parse_damage_string(dstr):
    
    if 'd' in dstr or 'D' in dstr:
        # typical format is 2d6+3
        if 'd' in dstr:
            parts = dstr.split('d')
        else:
            parts = dstr.split('D')
        num_rolls = int(parts[0])
        if '+' in parts[1]:
            parts2 = parts[1].split('+')
            die_range = (1,int(parts2[0]))
            extra = int(parts2[1])
        elif '-' in parts[1]:
            parts2 = parts[1].split('-')
            die_range = (1,int(parts2[0]))
            extra = -int(parts2[1])
        else:
            die_range = (1,int(parts[1]))
            extra = 0
    elif '-' in dstr:
        # format is 3-18
        parts = dstr.split('-')
        num_rolls = 1
        die_range = (int(parts[0]), int(parts[1]))
        extra = 0
    elif dstr.isdigit():
        # a single number
        num_rolls = 1
        die_range = (int(dstr),int(dstr))
        extra = 0
    else:
        num_rolls = 1
        die_range = (0,0)
        extra = 0

    return [num_rolls, die_range, extra]

               
def eval_free_move_to_tile(obj, lop, pos, game):
    allowed = True
    cost = 0
    map_section_name = obj.map_section
    map_section = game.map[map_section_name]
    if map_section[(pos)][0] == 'wall':
        allowed = False
    elif pos not in game.map_data[map_section_name]['known tiles']:
        allowed = False
    else:
        path, cost = aStar(lop, pos, obj, game, map_section_name)
        if cost >= impassable_tile_cost:
            allowed = False    
    
    return allowed, cost                
          
def ability_bonus(val):
    val = int(round(val))
    if val < 1:
        return None
    elif val <= 49:
        return ability_bonuses[val]
    else:
        base = ability_bonuses[49]
        dif = int(round(val-50))
        extra = 1 + dif/2
        return base+extra
        

def can_two_mobjs_talk(mobj1, mobj2, game):
    if can_one_mobj_speak_to_another(mobj1, mobj2, game) \
    and can_one_mobj_speak_to_another(mobj2, mobj1, game):
        return True
    else:
        return False
    
def can_one_mobj_speak_to_another(talker, hearer, game):
    if not talker.can_speak(game):
        return False           
    if not hearer.can_hear(game):
        return False
    if hearer.can_understand_all_languages(game):
        if len(talker.languages_spoken) >= 1:
            return True
    if talker.can_speak_all_languages(game):
        if len(hearer.languages_understood) >= 1:
            return True
    if set(talker.languages_spoken) & set(hearer.languages_understood):
        return True
    else:
        return False
    
# a dictionary to find the five tiles that one might flee to
# based on true opposite tile
#    1O2
#    3m4
#    xtx
# m is fleer, t is target fleeing from
# O is true opposite tile
# 1,2,3,4 are other 4    

#    (-1,-1)  (0,-1)  (+1,-1)
#    (-1,0)           (+1,0)
#    (-1,+1)  (0,+1)  (+1,+1)
five_flee_tiles = {}
five_flee_tiles[(-1,0)] = [(-1,0),(-1,+1),(-1,-1),(0,-1),(0,+1)]
five_flee_tiles[(-1,-1)] = [(-1,-1),(0,-1),(-1,0),(-1,+1),(+1,-1)]
five_flee_tiles[(0,-1)] = [(0,-1),(+1,-1),(-1,-1),(-1,0),(+1,0)]
five_flee_tiles[(+1,-1)] = [(+1,-1),(+1,0),(0,-1),(+1,+1),(-1,-1)]
five_flee_tiles[(+1,0)] = [(+1,0),(+1,-1),(+1,+1),(0,+1),(0,-1)]
five_flee_tiles[(+1,+1)] = [(+1,+1),(0,+1),(+1,0),(+1,-1),(-1,+1)]
five_flee_tiles[(0,+1)] = [(0,+1),(-1,+1),(+1,+1),(-1,0),(+1,0)]
five_flee_tiles[(-1,+1)] = [(-1,+1),(0,+1),(-1,0),(+1,+1,(-1,-1))] 
    
def find_flee_path(fleer,target,movement_points,game):
    # fleer (a mobj) is fleeing from target
    # find adjacent tile farthest away from target.pos
    path = []
    total_cost = 0.
    tpos = target.pos
    cpos = fleer.pos
#    cost_exceeded = False
    while True:
        opp_tile, opp_tile_relative = find_adj_tile_farthest_from_target(cpos, tpos)
        tiles_failed = 0
        for relative_tile_option in five_flee_tiles[opp_tile_relative]:
            tile = (relative_tile_option[0] + cpos[0], relative_tile_option[1]+cpos[1])
            if is_tile_passable(tile, fleer.map_section, game):
                cost = cost_to_adjacent(cpos, tile, fleer, game.map[fleer.map_section])
                if cost + total_cost <= movement_points:
                    total_cost += cost
                    path.append(tile)
                    cpos = tile
                    break
                else:
                    tiles_failed += 1
#                    cost_exceeded = True
#                    break
            else:
                tiles_failed += 1
        if tiles_failed >= 5:
            break
    return path
    
def is_tile_passable(pos,map_section_name,game):
    map_section = game.map[map_section_name]
    if pos not in map_section:
        return False
    else:
        tile_type = map_section[pos][0]
        terrainmod = TerrainMovementFactor[tile_type]
        if terrainmod == impassable_tile_cost:
            return False        
#        if tile_type == 'wall':
#            return False
        else:
            return True
            
def find_adj_tile_farthest_from_target(pos, target_pos):            
    mx = pos[0]
    my = pos[1]
    tx = target_pos[0]
    ty = target_pos[1]
    opp_tile = None
    if (ty-my == 0) or abs(tx-mx)/abs(ty-my) >= 2:
        if tx > mx:
            opp_tile = (mx-1,my)
        else:
            opp_tile = (mx+1,my)
    if (tx-mx == 0) or abs(ty-my)/abs(tx-mx) >= 2:
        if ty > my:
            opp_tile = (mx,my-1)
        else:
            opp_tile = (mx,my+1)
    if not opp_tile:
        if tx>mx:
            if ty>my:
                opp_tile = (mx-1,my-1)
            else:
                opp_tile = (mx-1,my+1)
        else:
            if ty>my:
                opp_tile = (mx+1,my-1)
            else:
                opp_tile = (mx+1,my+1)
    opp_tile_relative = (opp_tile[0]-mx,opp_tile[1]-my)
    return opp_tile, opp_tile_relative
                
        
def find_aura_power(obj):
    cleric_or_pal = False
    num_cp_hd = 0
    if hasattr(obj, 'advclasses'):
#    if isinstance (obj, class_based_mobile_object.ClassBasedMobj):
        if 'cleric' in obj.advclasses:
            num_cp_hd += obj.advclasses['cleric']
        if 'paladin' in obj.advclasses:
            num_cp_hd += obj.advclasses['paladin']
    num_hd = obj.find_total_level()
    
    if num_cp_hd >= 11:
        num_hd = num_cp_hd
        cleric_or_pal = True
    elif num_cp_hd >= 5:
        if num_hd < 51:
            num_hd = num_cp_hd
            cleric_or_pal = True
    elif num_cp_hd >= 2:
        if num_hd < 26:
            num_hd = num_cp_hd
            cleric_or_pal = True
    elif num_cp_hd >= 1:
        if num_hd < 11:
            num_hd = num_cp_hd
            cleric_or_pal = True
        
    aura = None
    if obj.type == 'outsider' or cleric_or_pal:
        if num_hd >= 11:
            aura = 'Overwhelming'
        elif num_hd > 5:
            aura = 'Strong'
        elif num_hd >= 2:
            aura = 'Moderate'
        else:
            aura = 'Faint'
    elif obj.type == 'undead':
        if num_hd >= 21:
            aura = 'Overwhelming'
        elif num_hd > 9:
            aura = 'Strong'
        elif num_hd >= 3:
            aura = 'Moderate'
        else:
            aura = 'Faint'
    elif hasattr(obj, 'race'):  # a creature
#    elif isinstance( obj, mobile_object.MobileObject ):     
        if num_hd >= 51:
            aura = 'Overwhelming'
        elif num_hd > 26:
            aura = 'Strong'
        elif num_hd >= 11:
            aura = 'Moderate'
        elif num_hd >= 5:
            aura = 'Faint'
    else:           # a magic item.  Assumes num_hd = caster level that created item
                    # todo - need to check this
        if num_hd >= 21:
            aura = 'Overwhelming'
        elif num_hd > 16:
            aura = 'Strong'
        elif num_hd >= 11:
            aura = 'Moderate'
        elif num_hd >= 6:
            aura = 'Faint'
    return aura
    
def find_spell_aura_power(spell, e_source, game):
    aura = None
    if 'obj_id' in e_source:
        caster_id = e_source['obj_id']
        caster = game.objectIdDict[caster_id]
        caster_level = spell.find_caster_level(caster)
        if caster_level >= 21:
            aura = 'Overwhelming'
        elif caster_level >= 16:
            aura = 'Strong'
        elif caster_level >= 11:
            aura = 'Moderate'
        elif caster_level >= 6:
            aura = 'Faint'
    return aura
    
    
def find_undead_aura_power(obj):
    num_hd = obj.find_total_level()
    aura = None
    if num_hd >= 11:
        aura = 'Overwhelming'
    elif num_hd > 5:
        aura = 'Strong'
    elif num_hd >= 2:
        aura = 'Moderate'
    else:
        aura = 'Faint'
    return aura
    
    # check for language in common, don't forget 
    # to check and see if hearer knows all languages
    # (and talker can speak one language)
    # or talker can speak all languages 
    # (and hearer can speak one language)          


                
    # tell clients about:
    # new position
    # update light levels
    # update viewed tiles
    # update otherteam now vis, invis, obj vis, obj invis
    # nonmovers that now see mover
    # traps, damage from traps
    # new time
    # all but last 2 are in orddat list already.  Last 2 maybe should be?
    
    # does every squares changes have to be sent, or can some of these
    # be consolidated?

