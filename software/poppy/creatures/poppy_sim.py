#!/usr/bin/env python
# coding: utf-8
"""
IPython Poppy Shell launcher

Author: aristofor - https://github.com/aristofor
"""

from pkg_resources import resource_filename
from IPython.config.loader import Config as ipConfig
from IPython.terminal.embed import InteractiveShellEmbed
from poppy.creatures import installed_poppy_creatures
from argparse import ArgumentParser
import sys


def launch_creature(name, vrep):
    """
    Loads creature's class and launches a shell.
    """
    poppy_args = {}
    if vrep:
        poppy_args['simulator'] = 'vrep'
    poppy = installed_poppy_creatures[name](**poppy_args)
    with open(resource_filename('poppy', 'logo.ascii')) as f:
        poppy_welcome = f.read()

    poppy_welcome += 'Poppy creature: {}'.format(name)
    cfg = ipConfig()
    cfg.TerminalInteractiveShell.confirm_exit = False
    shell = InteractiveShellEmbed(banner2=poppy_welcome)

    shell()


def main():
    """
    Entry point
    """
    parser = ArgumentParser(description='IPython Poppy Shell launcher.')

    parser.add_argument(dest='creature', type=str,
                        help="poppy creature name",
                        action="store", nargs='?',
                        choices=installed_poppy_creatures.keys())

    parser.add_argument('--vrep',
                        action='store_true',
                        help='use a V-REP simulated Poppy Creature')

    args = parser.parse_args()

    if not args.creature:
        if len(installed_poppy_creatures.keys()) == 1:
            args.creature = installed_poppy_creatures.keys()[0]
            print('No creature specified, use {}'.format(installed_poppy_creatures.keys()[0]))
        else:
            parser.print_help()
            sys.exit(0)
    launch_creature(args.creature, args.vrep)
