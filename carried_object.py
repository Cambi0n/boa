import game_object as gobj

class CarriedObject(gobj.GameObject):
    def __init__(self,**params):


        params.setdefault('equippable',False)
        self.equippable = params['equippable']
        params.setdefault('carried',False)
        self.carried = params['carried']
        params.setdefault('equipped',False)
        self.equipped = params['equipped']
        params.setdefault('on_ground',False)
        self.on_ground = params['on_ground']    # it is possible for an object to be neither carried, equipped, or on ground
                                                # such as when it is being dragged around on inventory screen
        params.setdefault('effect_if_equipped',False)
        self.effect_if_equipped = params['effect_if_equipped']
        params.setdefault('effect_if_carried',False)
        self.effect_if_carried = params['effect_if_carried']
#        params.setdefault('effect_details',[])
#        self.effect_details = params['effect_details']
        params.setdefault('effect_func_dict',{})        # keys are 'bonus','mult','binary'. 
                                                        # value is a list of strings of function names within item class
        self.effect_func_dict = params['effect_func_dict']

        melee_damage_dict = {}
        melee_damage_dict[0] = ('1d2','blunt')
        params.setdefault('melee_damage', melee_damage_dict)
        self.melee_damage = params['melee_damage']
        
        thrown_damage_dict = {}
        thrown_damage_dict[0] = ('1d2','blunt')
        params.setdefault('thrown_damage', thrown_damage_dict)
        self.thrown_damage = params['thrown_damage']

        params.setdefault('objtype','carried_item')
        
        gobj.GameObject.__init__(self,**params)
        

#        params.setdefault('damage1','1d6')
#        self.damage1 = params['damage1']
#        
#        params.setdefault('damage1type','slash')
#        self.damage1type = params['damage1type']
#        
#        params.setdefault('damage2',None)
#        self.damage2 = params['damage2']
#        
#        params.setdefault('damage2type','slash')
#        self.damage2type = params['damage2type']
        
#        params.setdefault('numhands',1)
#        self.numhands = params['numhands']
#        
#        params.setdefault('offhand_allowed',False)
#        self.offhand_allowed = params['offhand_allowed']
