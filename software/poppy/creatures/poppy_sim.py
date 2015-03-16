#!/usr/bin/env python
# coding: utf-8
"""
V-REP Simulation / iPython launcher
"""

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


def launch_creature(name):
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

    ns = { 'poppy' : cls(simulator='vrep') }
    banner = 'poppy : {}'.format(cls.__name__)
    cfg = ipConfig()
    cfg.TerminalInteractiveShell.confirm_exit = False
    shell = InteractiveShellEmbed(config=cfg, user_ns=ns, banner2=banner)
    shell()


def main():
    """
    Entry point
    """
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Poppy V-REP simulation/iPython launcher.')
    parser.add_argument('-l', '--list', help="List poppy creatures", action="store_true")
    parser.add_argument(dest='creature', help="Poppy creature name", action="store", nargs='?')

    args = parser.parse_args()

    if args.list:
        list_creatures()
    elif args.creature:
        launch_creature(args.creature)
    else:
        parser.print_help()
