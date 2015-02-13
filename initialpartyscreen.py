#import wx
#import wx.combo

import threading
import os

from twisted.internet import reactor

from twiststart import *

import pygame
from pgu import gui
import pguutils as pguu

#from network import *
#from netfunctions import *
#from wxcustom import *
from internalconstants import *
from userconstants import *
#from events import *
from fontdefs import *
import boautils as boaut
import saveload as sl


class InitialPartyScreen(gui.Table):
    def __init__(self, pgua, evManager, amihost, ismulti, profname, **params):
        gui.Table.__init__(self, **params)
        self.pgua = pgua

        self.evManager = evManager
        listencats = []
        self.evManager.RegisterListener( self, listencats )

        self.amihost = amihost
        self.ismulti = ismulti
        self.profname = profname
        self.profdir = os.path.join(profilespath,self.profname)

        self.maxnumchars = 8
        self.nextopenslot = 0

        self.ipsdata = {}
        self.ipsdata['all'] = []
        self.ipsdata['name'] = []
        self.ipsdata['class'] = []
        self.ipsdata['level'] = []
        self.ipsdata['controller'] = []
        for nc in range(self.maxnumchars):
            self.ipsdata['all'].append(-1)
            self.ipsdata['name'].append(-1)
            self.ipsdata['class'].append(-1)
            self.ipsdata['level'].append(-1)
            self.ipsdata['controller'].append(-1)

#        self.mfont = pygame.font.Font(resourcepath + 'freebooter.ttf',26)

        self.inpstyle = {}
        self.inpstyle['font'] = fontfbtr26
        self.inpstyle['background'] = (45,45,170)
        self.inpstyle[('background','focus')] = (75,75,220)
        self.inpstyle[('background','hover')] = (60,60,190)
        self.inpstyle['color'] = (200,200,200)
        
        self.textstyle = {}
        self.textstyle['font'] = fontfbtr26
        self.textstyle['background'] = (30,30,140)
        self.textstyle['color'] = (200,200,200)
        
        self.labelstyle = {}
        self.labelstyle['font'] = fontfbtr26
        self.labelstyle['background'] = (25,25,130)
        self.labelstyle['color'] = (200,200,200)
        self.labelstyle['padding_left'] = 6
        self.labelstyle['padding_right'] = 6
        self.labelstyle['padding_top'] = 3
        self.labelstyle['padding_bottom'] = 3

        self.labelstyle2 = {}
        self.labelstyle2['font'] = fontfbtr26
        self.labelstyle2['background'] = (25,25,130)
        self.labelstyle2['color'] = (255,215,0)
        self.labelstyle2['padding_left'] = 6
        self.labelstyle2['padding_right'] = 6
        self.labelstyle2['padding_top'] = 3
        self.labelstyle2['padding_bottom'] = 3
        
        self.listcharsondisk()
        
        if self.ismulti:
            if self.amihost:
                self.tgs = TwistGameStart(1, self.evManager, profname)
                reactor.callFromThread(self.tgs.Listen)
                self.InitialPartyScreenLayout(self.ipsdata)
            else:
                self.tgs = TwistGameStart(0, self.evManager, profname)
                self.EnterIP()
        else:
            self.InitialPartyScreenLayout(self.ipsdata)

    def EnterIP(self):
        ipt = gui.Table(background = (20,20,80))

        ipw = gui.Input(value = '127.0.0.1', size = 30, style = self.inpstyle, align = 0)
        ipt.td(ipw)
        
        ipt.tr()
        ipt.td(gui.Spacer(width = 1, height = 36))
        ipt.tr()
        EnterBtn = gui.Button("Enter")
        EnterBtn.connect(gui.CLICK, self.StartClient, ipw.value)
        ipt.td(EnterBtn)
        
        self.pgua.init(ipt)

    def StartClient(self, ip):
        reactor.callFromThread(self.tgs.Cnct, ip)
        
    def listcharsondisk(self):
        self._count = 0
        self.charfilenames = boaut.listFiles(self.profdir)
        self.char_list = gui.List(width=150, height=200)
        if self.charfilenames:
            for cname in self.charfilenames:
                self._count += 1
                self.char_list.add(cname, value = self._count)

    def InitialPartyScreenLayout(self, ipsdata):

        self.clear()
        self.ipsdata = ipsdata
        
        self.tr()        
        self.td(pguu.LabelMinSpace("Characters", style = self.labelstyle))
        self.td(pguu.LabelMinSpace("Party", style = self.labelstyle), colspan = 11)
        
        self.tr()
        
#            self.prof_list.items[0].click()
#            self.prof_list.items[0].pcls = 'down'
            
#            self.SetSelectedProfile()

        
        self.td(self.char_list, rowspan = self.maxnumchars+1)
        
        
        widthspacer = 22
        heightspacer = 12
        
        self.td(gui.Spacer(width = widthspacer, height = 1))
        self.td(gui.Spacer(width = widthspacer, height = 1))
        self.td(pguu.LabelMinSpace("Name", style = self.labelstyle))
        self.td(gui.Spacer(width = widthspacer, height = 1))
        self.td(pguu.LabelMinSpace("Class", style = self.labelstyle))
        self.td(gui.Spacer(width = widthspacer, height = 1))
        self.td(pguu.LabelMinSpace("Level", style = self.labelstyle))
        self.td(gui.Spacer(width = widthspacer, height = 1))
        self.td(pguu.LabelMinSpace("Controller", style = self.labelstyle))
        self.td(gui.Spacer(width = widthspacer, height = 1))
        self.td(pguu.LabelMinSpace("Remove", style = self.labelstyle))
        
        charsinparty = 0
        for i in range(self.maxnumchars):
            self.tr()
            self.td(pguu.LabelMinSpace(str(i+1), style = self.labelstyle))
            if self.ipsdata['all'][i] != -1:
                self.td(gui.Spacer(width = widthspacer, height = 1))
                self.td(pguu.LabelMinSpace(self.ipsdata['name'][i], style = self.labelstyle2))
                self.td(gui.Spacer(width = widthspacer, height = 1))
                self.td(pguu.LabelMinSpace(self.ipsdata['class'][i].keys()[0], style = self.labelstyle2))
                self.td(gui.Spacer(width = widthspacer, height = 1))
                self.td(pguu.LabelMinSpace(str(self.ipsdata['class'][i].values()[0]), style = self.labelstyle2))
                self.td(gui.Spacer(width = widthspacer, height = 1))
                self.td(pguu.LabelMinSpace(self.ipsdata['controller'][i], style = self.labelstyle2))
                self.td(gui.Spacer(width = widthspacer, height = 1))
                btn = gui.Button("Remove")
                self.td(btn)
                if self.ipsdata['controller'][i] == self.profname or self.amihost:
                    btn.connect(gui.CLICK, self.preremovecharfromparty, i)
                else:
                    btn.disabled = True
                charsinparty += 1
                

        self.tr()
        self.addbtn = gui.Button("Add To Party")
        self.td(self.addbtn)
        self.addbtn.connect(gui.CLICK,self.preaddtoparty)
        if charsinparty >= 8:
            self.addbtn.disabled = True
        else:
            self.addbtn.disabled = False
        
        self.tr()
        self.td(gui.Button("Create New Character"))
        
        if self.amihost:
            self.tr()
            self.td(gui.Spacer(height = 24, width = 1))
            self.tr()
            ReadyBtn = pguu.BmpButton(gui.Image(resourcepath + "ready.png"), theme = 'gui2theme')
            ReadyBtn.SetBmp(gui.Image(resourcepath + "readyhover.png"), 'hover')
            ReadyBtn.SetBmp(gui.Image(resourcepath + "readydown.png"), 'down')
#            self.td(ReadyBtn, col = 6, align = 1)
            self.td(ReadyBtn, col = 9, colspan = 3)
            ReadyBtn.connect(gui.CLICK, self.OnReady)
        
        self.pgua.init(self)
        
        
    def preaddtoparty(self):
        #todo - check for unique profile names, or modify profiles names so they are unique (e.g. bdf(2) )
        charidx = self.char_list.value
        print 'preadding', charidx, self.charfilenames[charidx-1]
        if charidx:
            charfilename = self.charfilenames[charidx-1]
            
            thisAdv = sl.loadhero(self.profdir, charfilename)
#            shortdat = [thisAdv.name, thisAdv.advclass, thisAdv.level, self.profname]
            if self.ismulti and not self.amihost:
                reactor.callFromThread(self.tgs.evalAddChar, thisAdv, self.profname)
            else:
                self.evaladdtoparty(thisAdv, self.profname)
                    
    def evaladdtoparty(self, Adv, profname):
        # only host executes this
        alreadyinparty = False
        charfilename = Adv.name
        for i in range(self.maxnumchars):
            if charfilename == self.ipsdata['name'][i]:
                alreadyinparty = True
                break
        if not alreadyinparty:
            self.addtoparty(Adv, profname)
                    
    def addtoparty(self, Adv, profname):
        #only host executes this
        nos = self.nextopenslot
        self.ipsdata['all'][nos] = Adv
        self.ipsdata['name'][nos] = Adv.name
        self.ipsdata['class'][nos] = Adv.advclasses
#        self.ipsdata['level'][nos] = Adv.level
        self.ipsdata['controller'][nos] = profname
        self.nextopenslot += 1
        
        if self.ismulti and self.amihost:
            reactor.callFromThread(self.tgs.distributeIPSdata, self.ipsdata)
            
        self.InitialPartyScreenLayout(self.ipsdata)
        
    def preremovecharfromparty(self, slot):
        charname = self.ipsdata['name'][slot]
        if self.ismulti and not self.amihost:
            reactor.callFromThread(self.tgs.evalRemoveChar, charname)   
        else:
            self.evalremovecharfromparty(charname)
            
    def evalremovecharfromparty(self,charname):
        #only host executes this
        slot = -1
        for i in range(self.maxnumchars):
             if charname == self.ipsdata['name'][i]:
                 slot = i
                 break
        if slot >= 0:
            self.removecharfromparty(slot)
        
    def removecharfromparty(self, slot):
        #only host executes this
        for i in range(slot,self.nextopenslot-1):
            self.ipsdata['all'][i] = self.ipsdata['all'][i+1]
            self.ipsdata['name'][i] = self.ipsdata['name'][i+1]
            self.ipsdata['class'][i] = self.ipsdata['class'][i+1]
            self.ipsdata['level'][i] = self.ipsdata['level'][i+1]
            self.ipsdata['controller'][i] = self.ipsdata['controller'][i+1]
            
        self.ipsdata['all'][self.nextopenslot-1] = -1
        self.ipsdata['name'][self.nextopenslot-1] = -1
        self.ipsdata['class'][self.nextopenslot-1] = -1
        self.ipsdata['level'][self.nextopenslot-1] = -1
        self.ipsdata['controller'][self.nextopenslot-1] = -1
        self.nextopenslot -= 1

        if self.ismulti and self.amihost:
            reactor.callFromThread(self.tgs.distributeIPSdata, self.ipsdata)
            
        self.InitialPartyScreenLayout(self.ipsdata)

    def OnReady(self):

        if self.ismulti:
            reactor.callFromThread(self.tgs.SwitchToMainNWM, self.ipsdata, self.evManager)
        else:
            hnf = HostNetFunctions(None, self.evManager, self.profname)
            cnf = ClientNetFunctions(None, self.evManager, True)
            cnf.givehnf(hnf)
            
            eV = SetHostAndProfAndIpsdata( 1, self.profname, self.ipsdata, False )
            queue.put(eV)
            
            eV = InitScreenDoneEvent()
            queue.put(eV)

    def HostReceivedNewPlayer(self):
        # executed only by host.  Nothing needs to happen here any more.
        # maybe print a message on everybody's screen that a new player has joined
        
        print 'hrnp'
        reactor.callFromThread(self.tgs.distributeIPSdata, self.ipsdata)

        
    def Notify(self, event):

        if isinstance( event, HostReceivedNewPlayer ):
            self.HostReceivedNewPlayer()
        
        elif isinstance( event, EvaluateStartChoice ):
            self.EvaluateChoice(event.widget, event.catrow, event.choice, event.ctrl)
            
        elif isinstance( event, EvalAddChar ):
            self.evaladdtoparty(event.Adv, event.profname)
            
        elif isinstance( event, EvalRemoveChar ):
            self.evalremovecharfromparty(event.charname)
            
        elif isinstance( event, InitpartyScreenLayout):
#            self.clear()
            self.InitialPartyScreenLayout(event.ipsdata)
            
        elif isinstance( event, clientClearMPStartupScreenEvent):
            self.clearScreen()

