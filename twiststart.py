import threading

from twisted.internet import reactor
from twisted.spread import pb
from twisted.python import threadable
threadable.init(1)

from network import *
from netfunctions import *
try:
    import cPickle as pickle
except:
    import pickle

class TwistLoop(threading.Thread):
    def __init__(self):
        super(TwistLoop, self).__init__()

    def run(self):
        # Dummy demo stuff
        #reactor.callLater(3, self.helloWorld)

        #def twoSecondsPassed():
            #print "two seconds passed"
        #reactor.callLater(2, twoSecondsPassed)

        # Run reactor
        reactor.run(installSignalHandlers=0)

class InitHostNetworkManager(pb.Root):
    def __init__(self):
#        self.profname = profname
#        self.mps = mps
        self.icNWMlist = []  # list will contain all other iNWMs, but not own
        #self.hNWM = 0   # nonzero if host
        self.numcNWMs_inhostlist = 0
        
#        self.prof_cnwm_dict = {}
#        self.prof_cnwm_dict[profname] = []
#        self.prof_cnwm_dict[profname].append(-1) 


    def remote_iNWMToHost(self, icNWM):
        if icNWM not in self.icNWMlist:
            self.icNWMlist.append(icNWM)
            #todo - need to remove from this list if client leaves

            print 'receiving inwm', threading.currentThread()

            # find next open slot
            '''
            slotnum = -1
            for i in range(self.mps.maxnumplayers):
                if self.mps.mpdata['control'][i] == -1:
                    slotnum = i
                    break
            if slotnum == -1:
                raise NoFreeSlotsError
            '''
            
            # send new player's slot back to new player
#            icNWM.callRemote("SlotToClient", slotnum)

            ev = HostReceivedNewPlayer()
            queue.put(ev)
            
#            self.mps.HostReceivedNewPlayer(slotnum, clientMPdata)
#            wx.CallAfter(self.mps.HostReceivedNewPlayer, slotnum, clientMPdata)

            #self.mpscreen.UpdateMpformFromMpdataAll()  # update host form with new player

#    def DistributeNewMpdata(self, mpdata):
#        for iN in self.icNWMlist:
#            # send new iNWM to all clients
#            #if iN != iNWM:
#            #   iN.callRemote("newiNWMtoClients", iNWM)
#            #send currently known mpdata back to all players
#            iN.callRemote("AllMpdataToClient", mpdata)

#    def remote_ProposeChoice(self, categ, row, choice, ctrl):
##        wx.CallAfter(self.mps.EvaluateChoice, 0, categ, row, choice, ctrl)
#
#        ev = EvaluateStartChoice(0,(categ, row), choice, ctrl)
#        queue.put(ev)
##        self.mps.EvaluateChoice(0, (categ, row), choice, ctrl)

    def remote_EvaladdChar(self, pAdv, profname):
#        profnotinyet = True
#        for prof in self.prof_icnwm_dict.keys():
#            if prof == profname:
#                profnotinyet = False
#                break
#        if profnotinyet:
#            self.prof_icnwm_dict[profname] = []
#            self.prof_icnwm_dict[profname].append(icnwm)
        Adv = pickle.loads(pAdv)    
        ev = EvalAddChar(Adv, profname)
        queue.put(ev)

    def remote_EvalremoveChar(self, charname):
        ev = EvalRemoveChar(charname)
        queue.put(ev)

    def Distributeipsdata(self, ipsdata):
        pips = pickle.dumps(ipsdata, pickle.HIGHEST_PROTOCOL)
        for iN in self.icNWMlist:
            # send new iNWM to all clients
            #if iN != iNWM:
            #   iN.callRemote("newiNWMtoClients", iNWM)
            #send currently known mpdata back to all players
            iN.callRemote("IPSdataToClient", pips)

    def sendClearMPStartupScreen(self):
        for iN in self.icNWMlist:
            iN.callRemote("clientClearMPStartupScreen")

    def HostobjectsToClients(self, hNWM, ipsdata):
        self.hNWM = hNWM
        self.ipsdata = ipsdata
        for iN in self.icNWMlist:
            iN.callRemote("SendhNWMtoClients", hNWM)

    def remote_SendcNWMtoHost(self, cNWM, cprofname):
        self.hNWM.hnf.addcNWM(cNWM, cprofname)
        self.numcNWMs_inhostlist += 1
        if self.numcNWMs_inhostlist >= len(self.icNWMlist):
            pips = pickle.dumps(self.ipsdata, pickle.HIGHEST_PROTOCOL)
            for iN in self.icNWMlist:
                iN.callRemote("HaveAllcNWMs_sigToClients", pips)

class InitClientNetworkManager(pb.Referenceable):
    def __init__(self, evManager, profname):
#        self.mps = mps
        self.evManager = evManager
        self.hostiNWM = 0   # this remains zero for host, host iNWM object for all others
        #self.ownNWM = 0 # nonzero if not host
        
        self.profname = profname

    def sethostiNWM(self, returnedhostiNWM):
        self.hostiNWM = returnedhostiNWM

#    def remote_SlotToClient(self, slot):
#        self.mps.myslot = slot      # there is no other place where data is assigned
                                    # to myslot, so go ahead and access it directly
        #self.mpscreen.EnableMySlot(slot)

    def remote_IPSdataToClient(self, pips):
        #print 'AMTC', mpdata
        #self.mps.mpdata = mpdata
#        wx.CallAfter(self.mps.MultiplayerScreenLayout, mpdata)
        ipsdata = pickle.loads(pips)
        ev = InitpartyScreenLayout(ipsdata)
        queue.put(ev)
#        self.mps.MultiplayerScreenLayout(mpdata)
        #self.mpscreen.UpdateMpformFromMpdataAll()

#    def remote_NewMPdataToClient(self, mpdata):
#        #print 'AMTC', mpdata
#        #self.mps.mpdata = mpdata
#        ev = MultiplayerScreenLayout(mpdata)
#        queue.put(ev)
##        self.mps.clear()
##        self.mps.MultiplayerScreenLayout(mpdata)
##        wx.CallAfter(self.mps.SetNewVals, mpdata)
#        #self.mpscreen.UpdateMpformFromMpdataAll()

    def remote_clientClearMPStartupScreen(self):
        ev = clientClearMPStartupScreenEvent()
        queue.put(ev)
        
    def remote_SendhNWMtoClients(self, hNWM):
        self.ownNWM = ClientNetworkManager()
        cnf = ClientNetFunctions(self.ownNWM, self.evManager, False)
        cnf.addhNWM(hNWM)
        self.ownNWM.givecnf(cnf)
        self.hostiNWM.callRemote("SendcNWMtoHost", self.ownNWM, self.profname)

    def remote_HaveAllcNWMs_sigToClients(self, pips):

        ipsdata = pickle.loads(pips)
        eV = SetHostAndProfAndIpsdata( 0, self.profname, ipsdata, True )
        queue.put(eV)

        ev = WaitForAllClients(self.profname)
        queue.put(ev)


class TwistGameStart:
    def __init__(self, amhost, evManager, profname):
        self.amhost = amhost
        self.evManager = evManager
        self.profname = profname
#        self.mps = mps

        if self.amhost:
            self.ihNWM = InitHostNetworkManager()
        else:
            self.icNWM = InitClientNetworkManager(self.evManager, profname)
            self.factory = pb.PBClientFactory()

    def Listen(self):
        reactor.listenTCP(8800, pb.PBServerFactory(self.ihNWM))
        print 'listening', threading.currentThread()

    def Cnct(self, hostipnum):
        reactor.connectTCP(hostipnum, 8800, self.factory)

        def1 = self.factory.getRootObject()
        def1.addCallbacks(self.got_obj1, self.err_obj1)

    def err_obj1(self, reason):
        print "error getting first object", reason
        reactor.stop()

    def got_obj1(self, returnedhostiNWM):
        self.hostiNWM = returnedhostiNWM    # set it for this class
        print 'got it', threading.currentThread()
        self.icNWM.sethostiNWM(returnedhostiNWM) # set it for client iNWM class
        self.hostiNWM.callRemote("iNWMToHost", self.icNWM) # send own iNWM to host

#    def DistributeNewclientData(self, mpdata):
#        self.ihNWM.DistributeNewMpdata(mpdata)

#    def EvalChoice(self, categ, row, choice, ctrl):
#        self.hostiNWM.callRemote("ProposeChoice", categ, row, choice, ctrl)

#    def DistributeMPData(self, mpdata):
#        self.ihNWM.DistributeMPdata(mpdata)

    def clearMPStartupScreen(self):
        self.ihNWM.sendClearMPStartupScreen()
        
    def evalAddChar(self, Adv, profname):
        pAdv = pickle.dumps(Adv, pickle.HIGHEST_PROTOCOL)
        self.hostiNWM.callRemote("EvaladdChar", pAdv, profname)

    def evalRemoveChar(self, charname):
        self.hostiNWM.callRemote("EvalremoveChar", charname)
        
    def distributeIPSdata(self, ipsdata):
        self.ihNWM.Distributeipsdata(ipsdata)

    def SwitchToMainNWM(self, ipsdata, evManager):
        hNWM = HostNetworkManager()
        hnf = HostNetFunctions(hNWM, evManager, self.profname)
        hNWM.givehnf(hnf)
        self.ihNWM.HostobjectsToClients(hNWM, ipsdata)

        cnf = ClientNetFunctions(hNWM, evManager, True)
        cnf.givehnf(hnf)
        hnf.givecnf(cnf)

        numclients = len(self.ihNWM.icNWMlist) + 1
        eV = SetHostAndProfAndIpsdata( 1, self.profname, ipsdata, True, numclients )
        queue.put(eV)
        
        eV = WaitForAllClients(self.profname, 'Init Screen Done')
        queue.put(eV)






