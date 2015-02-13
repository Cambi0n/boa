import spells1
import spells2

def complete_dict_of_spells():
    spell_list = {}
    spell_list['magic_missile'] = spells1.MagicMissile()
    spell_list['mage_armor'] = spells1.MageArmor()
    spell_list['bane'] = spells2.Bane()
    spell_list['bless'] = spells2.Bless()
    spell_list['bless_water'] = spells2.BlessWater()
    spell_list['cause_fear'] = spells2.CauseFear()
    spell_list['command'] = spells2.Command()
    spell_list['comprehend_languages'] = spells2.ComprehendLanguages()
    spell_list['cure_light_wounds'] = spells2.CureLightWounds()
    spell_list['curse_water'] = spells2.CurseWater()
    spell_list['deathwatch'] = spells2.Deathwatch()
    spell_list['detect_chaos'] = spells2.DetectChaos()
    spell_list['detect_law'] = spells2.DetectLaw()
    spell_list['detect_evil'] = spells2.DetectEvil()
    spell_list['detect_good'] = spells2.DetectGood()
    spell_list['detect_undead'] = spells2.DetectUndead()
    spell_list['divine_favor'] = spells2.DivineFavor()
    spell_list['doom'] = spells2.Doom()
    spell_list['entropic_shield'] = spells2.EntropicShield()
    spell_list['hide_from_undead'] = spells2.HideFromUndead()
    
    return spell_list    


