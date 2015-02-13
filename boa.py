#import Queue

import pygame
from pygame.locals import *
from pgu import gui
from internalconstants import *

def startPyGame():

    pygame.display.init()
    pygame.font.init()
    pygame.mixer.init()

#    #from events import *
    import evmanager as evm
#    #from game import *
    import controllers as cntrls
    import mainview as mv
    import unitview as uv
    import townview as tv
    import pgucontrol as pguc
    import startup as strtup

    
    wind = pygame.display.set_mode( screenres, screenflag )
        
#    pygame.surfarray.use_arraytype('numpy')

    evManager = evm.EventManager()
        
    pguapp = gui.App(theme = default_theme)
    pguapp.add_theme("gui2theme")
    
    pguctrl = pguc.pguControl(pguapp, evManager, wind)

    mainView = mv.MainView( evManager, wind, pguapp, pguctrl )
    uv.UnitView(evManager, mainView, pguctrl)
#    tv.TownView(evManager, pguctrl)
    mastercontroller = cntrls.MasterController( evManager, mainView, pguapp, pguctrl )

    pguctrl.CreatePanels(mainView)
    
    strtup.ShowFirstScreen(evManager, pguapp)

    mastercontroller.Run()

def main():
    startPyGame()

if __name__ == '__main__':
    main()

