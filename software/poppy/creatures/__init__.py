import sys
import pip

from abstractcreature import AbstractPoppyCreature


def installed_poppy_creatures_packages():
    return [p.key for p in pip.get_installed_distributions()
            if p.key.startswith('poppy-') and p.key != 'poppy-creature']

module = sys.modules[__name__]

installed_poppy_creatures = {}

for creature in installed_poppy_creatures_packages():
    package = creature.replace('-', '_')
    cls_name = ''.join(x.capitalize() or '_' for x in package.split('_'))

    try:
        cls = getattr(__import__(package), cls_name)
        installed_poppy_creatures[creature] = cls
        setattr(module, cls_name, cls)

    except (ImportError, AttributeError):
        pass
