#import pygame
#from pygame.locals import *
import os
import Queue
queue = Queue.Queue()
orders_timed_event_list = []        # for timed events related to object orders
effects_timed_event_list = []     # for start and end of various effects
other_timed_event_list = []

hctp_orddat = []        # hostcomplete to player orders data
np = 0      # number of pulse for hctp_orddat

DIRECTION_UP = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN = 2
DIRECTION_LEFT = 3

debug_on = 1
#singleplayer = 1

#screenres = (1024,768)
#screenflag = pygame.FULLSCREEN
#screenres = (1024,768)
#screenflag = 0
screenres = (1024,768)
toppanel_height = 64
bottom_window_heights = 200
screenflag = 0

default_theme = "guitheme"
resourcepath = os.path.join('data',"")
profilespath = os.path.join('profiles',"")
gamespath = os.path.join('games',"")
defaultgamepath = os.path.join(gamespath,'default',"")
levelspath =  os.path.join(defaultgamepath,'levels',"")
tilespath = os.path.join(resourcepath,'tiles')
terraintilespath = os.path.join(tilespath,'terrain')
playertilespath = os.path.join(tilespath,'player')
monstertilespath = os.path.join(tilespath,'monsters')
objecttilespath = os.path.join(tilespath,'objects')


