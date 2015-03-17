#!/usr/bin/env python
# coding: utf-8
"""
IPython Poppy Shell launcher

Author: aristofor - https://github.com/aristofor
"""

from pkg_resources import resource_filename
from IPython.config.loader import Config as ipConfig
from IPython.terminal.embed import InteractiveShellEmbed
import re
import sys

def load_poppy_creatures():
    """
    Loads poppy.creatures, returns a namespace containing creatures classes
    """
    import poppy.creatures
    result = []
    for x in dir(poppy.creatures):
        o = getattr(poppy.creatures, x)
        if isinstance(o,type) and issubclass(o,poppy.creatures.AbstractPoppyCreature) and o!=poppy.creatures.AbstractPoppyCreature:
            result.append(o)
    return result


def list_creatures():
    """
    Return the list of installed poppy-creature packages
    """
    ns = load_poppy_creatures()
    print("Poppy creatures :")
    for name in ns:
        shortcut = name.__name__[5:]
        print('    {}'.format(shortcut))


def launch_creature(name, vrep):
    """
    Loads creature's class and launches a shell.
    Note: name is case insensitive.
    """
    ns = load_poppy_creatures()
    cls = None
    for x in ns:
        # Strips leading 'Poppy'
        if x.__name__[5:].lower() == name.lower():
            cls = x

    if cls is None:
        sys.stderr.write("Creature not found : {}\n".format(name))
        sys.exit(1)

    poppy_args = {}
    if vrep:
        poppy_args['simulator'] = 'vrep'

    with open(resource_filename('poppy', 'logo.ascii')) as f:
        poppy_welcome = f.read()

    poppy_welcome += 'Poppy creature: {}'.format(name)

    ns = { 'poppy' : cls(**poppy_args) }
    banner = 'poppy : {}'.format(cls.__name__)
    cfg = ipConfig()
    cfg.TerminalInteractiveShell.confirm_exit = False
    shell = InteractiveShellEmbed(config=cfg, user_ns=ns, banner2=poppy_welcome)
    shell()


def main():
    """
    Entry point
    """
    from argparse import ArgumentParser
    parser = ArgumentParser(description='IPython Poppy Shell launcher.')

    parser.add_argument('-l', '--list',
                        help="List poppy creatures",
                        action="store_true")

    parser.add_argument('--vrep',
                        action='store_true',
                        help='Use a V-REP simulated Poppy Creature')

    parser.add_argument(dest='creature',
                        help="Poppy creature name",
                        action="store", nargs='?')

    args = parser.parse_args()

    if args.list:
        list_creatures()
    elif args.creature:
        launch_creature(args.creature, args.vrep)
    else:
        parser.print_help()
