timerspeed = 2
scroll_slowdown = 0
scroll_width = 1
scroll_jump = 40
normalmovieframedelay = 50

#AlwaysShowUnitModePopup = True

#mapdim = (150,150)  # (width, height) number of tiles, i.e. map size in game coordinates
#mapdim = (200,200)

wrap_East_West = False
wrap_North_South = False

# each tile is #pizels x #pizels in size
#tilepixsizes = [4, 8, 16, 32]
tilepixsize = 64

zoomfactors = [0.125, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]     # must be floating point
                                                            # one value must be 1.0
                                                            # 1.0 corresponds to each tile
                                                            # being tilepixsize x tilepixsize
                                                            # pixels
                                                            
#spritezoomfactors = [0.5, 0.5, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
spritezoomfactors = [0.125, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    # controls sprite size
    # must be same length as zoomfactors
    # a larger number than the corresponding zoomfactor entry means the sprite
    # image will take up more than one terrain square

turn_mode = 'we_go_they_go'     # all party members plot orders, then party orders are executed
                                # then monsters plot orders, then monster's orders are executed
                                # resulting in a total number of pulses equal to 2*num_pulses_per_unit.
                                # An alternative style of play is 'initiative' based (not implemented yet)
                                # For initiative based, each unit would plot a part of its turn, then
                                # that action would be executed, then another action plotted, another action
                                # executed until a unit's entire num_pulses_per_unit turn is finished.  Then 
                                # the next unit (or monster) would go.  The total number of pulses would be:
                                # num_pulses_per_unit*(num_adventurers + num_monsters).  If many monsters
                                # are present, it will probably be necessary to put groups of monsters into 
                                # the same "initiative slot" in order to keep the number of pulses to a 
                                # reasonable level.
                                
#free_move_mode_time_factor = 0.5   # ranges from 0.0 to 1.0.  Influences the rate that time moves forward during
                                    # 'free' move_mode.  When set to zero, a character in a party of 4 that would 
                                    # have used 6 seconds worth of movement during 'phased' move_mode (to say 
                                    # move 6 squares) would use 6*(1/4) seconds during 'free' move mode.  If set to 1.0,
                                    # the same movement would use 6 seconds.  Other settings are interpolated (between
                                    # 1.5 and 6 seconds).  The above example does not take into account that characters
                                    # 'walk' during 'free' move mode and 'hustle' (twice 'walk' speed) during 'phased' 
                                    # move mode.
free_move_to_phased_move_speed_fraction = 0.5   # in phased move mode, one is 'hustling', or moving twice
                                                # as fast as in free move mode

num_pulses_per_unit = 100.0
num_pulses_for_standard_action = 50.0   # move action is then num_pulses_per_unit - num_pulses_for_standard_action
                                        # used to time movements and actions during execution
num_pulses_for_move_action = 50.0  
seconds_per_round = 6

feedback_level = 1      # options are 0, 1, 2
                        # with 0, you will rarely see numbers for your attacks.  You will still see numbers
                        # for your personal attributes and hp, etc.
                        # with level 1, you will see your die rolls and damage you do and damage done to 
                        # you, but you won't see monsters hp and you won't see monsters rolls.  You will 
                        # be told in general terms about health of monster.
                        # with level 2, you will see all the numbers. 
# since movespeed is expressed in squares per turn,
# energy per square = numpulses * gameEnergyPerPulse / movespeed
# if a mobile object's energyperpulse increases, that object
# does *everything* faster - including fighting (energy per square 
# is based on the baseline energyperpulse, not the enhanced value).
# if movespeed increases, then energy per square goes down, but object 
# doesn't fight faster

# map colors
# 0 is water, 1 is plain, 2 is rough

#mapcolors = {0:(0,0,255),
            #1: (0,240,0),
            #2: (222,184,135)}

SHARED_SIGHT = True
# With SHARED_SIGHT True, everything one character sees is visible to
# all characters
# With SHARED_SIGHT False, mobile objects such as monsters are only shown
# to a character if they are visible to that character.  Also, the
# parts of a level that are currently visible to that character
# are indicated.  However, non-mobile dungeon features, such as
# walls, doors, and traps are still shown to all characters once one 
# character sees them. (False option not implemented yet)
BRIGHT_LIGHT_INTENSITY = 50
NORMAL_LIGHT_INTENSITY = 10
DIM_LIGHT_INTENSITY = 5
ULTRADIM_LIGHT_INTENSITY = 1
DARKVISION_RADIUS = 12

TERRAIN_BRIGHTNESS_INDICATES_LIGHT_LEVEL = False   # if False, then terrain
            # brightness indicates view level (dim or normal).  For example,
            # a tile might have a very low light level.  A human wouldn't be 
            # able to see anything in that tile.  But an elf might be able 
            # to have a dim view level into the tile.

#always_see_other_party_members = True

minimapcolors = {}
minimapcolors[('floor','underground1')] = ( (0,255,0) )
minimapcolors[('shallow_water','shallow1')] = ( (0,0,255) )
minimapcolors[('wall','granite')] = ( (50,50,50) )
minimapcolors[('wall with small opening','granite')] = ( (50,50,50) )
minimapcolors[('wall with large opening','granite')] = ( (50,50,50) )
minimapcolors[('low obstacle','granite')] = ( (50,50,50) )
minimapcolors[0]=( (0,0,255) )
minimapcolors[1]=( (0,0,255) )
minimapcolors[2]=( (0,0,255) )
minimapcolors[3]=( (0,0,255) )
minimapcolors[4]=( (0,255,0) )
minimapcolors[5]=( (0,128,0) )
minimapcolors[6]=( (139,90,43) )
minimapcolors[7]=( (139,90,43) )
minimapcolors[8]=( (255,255,255) )
minimapcolors[9]=( (255,255,255) )

maptiles = {}
maptiles[('floor','greyrock1')] = ['grass','water']
maptiles[('water','deep1')] = ['water']
maptiles[0]= ['water']
maptiles[1]= ['water']
maptiles[2]= ['water']
maptiles[3]= ['water']
maptiles[4]= ['grass']
maptiles[5]= ['grass']
maptiles[6]= ['grass']
maptiles[7]= ['grass']
maptiles[8]= ['grass']
maptiles[9]= ['grass']

nationColors = [(255,0,0), \
                (0,150,0), \
                (0,255,0), \
                (0,0,255), \
                (200,200,0), \
                (200,0,200), \
                (0,200,200), \
                (2,2,2), \
                (253,253,253)]

gcRed = (240,0,0)
gcDullRed = (120,0,0)
gcYellow = (240,240,0)
gcGreen = (0,240,0)
gcBlack = (0,0,0)
gcWhite = (255,255,255)
userconst_ordercolors = [gcGreen, gcYellow, gcRed]    # used to color order lines
userconst_ordertextcolor = [gcBlack, gcBlack, gcWhite]       # used for text on top of ordercolors
maxturnsorders = 20     # maximum number of turns of orders to be shown

splashscreencolor = (100, 100, 200)
infowindowbackgroundcolor = (100,100,100)

gameBaseMoveSpeed = 6.  # squares per round.  TerrainMovementFactor distinguishes between terrain
        # In initiative mode, this is the number of squares an object can move during a move action.
        # Thus a char can move twice this per round if they use both move and standard actions
        # for movement.  This represents 'hustle' movement speed.
        # In free_move mode, a character moves at a walk speed, which is half the speed of 'hustle'.
        # If running is called for, the game should go into initiative mode. 

impassable_tile_cost = 100000.0
# smaller is terrain one can move faster over
# The AStar path algorithm produces optimal paths if the smallest movement factor is 1
# the algorithm will run faster, but less accurately, if smallest movement factor is less than 1
TerrainMovementFactor = {}
TerrainMovementFactor['shallow_water'] = 2.0
TerrainMovementFactor['floor'] = 1.0
TerrainMovementFactor['wall'] = impassable_tile_cost
TerrainMovementFactor['wall with small opening'] = impassable_tile_cost
TerrainMovementFactor['wall with large opening'] = impassable_tile_cost
TerrainMovementFactor['low obstacle'] = 2.0


ability_bonuses = {}
ability_bonuses[1] = -5
ability_bonuses[2] = -4
ability_bonuses[3] = -4
ability_bonuses[4] = -3
ability_bonuses[5] = -3
ability_bonuses[6] = -2
ability_bonuses[7] = -2
ability_bonuses[8] = -1
ability_bonuses[9] = -1
ability_bonuses[10] = 0
ability_bonuses[11] = 0
ability_bonuses[12] = 1
ability_bonuses[13] = 1
ability_bonuses[14] = 2
ability_bonuses[15] = 2
ability_bonuses[16] = 3
ability_bonuses[17] = 3
ability_bonuses[18] = 4
ability_bonuses[19] = 4
ability_bonuses[20] = 5
ability_bonuses[21] = 5
ability_bonuses[22] = 6
ability_bonuses[23] = 6
ability_bonuses[24] = 7
ability_bonuses[25] = 7
ability_bonuses[26] = 8
ability_bonuses[27] = 8
ability_bonuses[28] = 9
ability_bonuses[29] = 9
ability_bonuses[30] = 10
ability_bonuses[31] = 10
ability_bonuses[32] = 11
ability_bonuses[33] = 11
ability_bonuses[34] = 12
ability_bonuses[35] = 12
ability_bonuses[36] = 13
ability_bonuses[37] = 13
ability_bonuses[38] = 14
ability_bonuses[39] = 14
ability_bonuses[40] = 15
ability_bonuses[41] = 15
ability_bonuses[42] = 16
ability_bonuses[43] = 16
ability_bonuses[44] = 17
ability_bonuses[45] = 17
ability_bonuses[46] = 18
ability_bonuses[47] = 18
ability_bonuses[48] = 19
ability_bonuses[49] = 19
