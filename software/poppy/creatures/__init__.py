import sys

from .abstractcreature import AbstractPoppyCreature

module = sys.modules[__name__]


installed_poppy_creatures = {}
existing_creatures = ['poppy-humanoid', 'poppy-torso', 'poppy-ergo-jr']


for creature in existing_creatures:
    package = creature.replace('-', '_')
    cls_name = ''.join(x.capitalize() or '_' for x in package.split('_'))

    try:
        cls = getattr(__import__(package), cls_name)
        installed_poppy_creatures[creature] = cls
        setattr(module, cls_name, cls)

    except (ImportError, AttributeError):
        pass
