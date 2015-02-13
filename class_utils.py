
def find_caster_level(caster,spell):
    caster_level = 0
    for c,l in caster.advclasses.iteritems():
        if c in spell.classes:
            caster_level += l
    return caster_level