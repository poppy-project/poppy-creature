#!/usr/bin/env python

from __future__ import print_function

import sys
import time
import random
import logging
import argparse
import webbrowser

from argparse import RawTextHelpFormatter

from pypot.server.snap import find_local_ip

from . import installed_poppy_creatures


def start_poppy_with_services(args):
    params = poppy_params_from_args(args)

    for _ in range(5):
        try:
            return installed_poppy_creatures[args.creature](**params)

        except KeyboardInterrupt:
            # In case of failure,
            # Give the robot some time to statup, reboot...
            time.sleep(random.random())
    else:
        print('Could not start up the robot...')
        sys.exit(1)

    return poppy


def poppy_params_from_args(args):
    params = {
        'use_snap': args.snap,
        'use_http': args.http,
        'use_remote': args.remote
    }

    if args.verbose:
        params['snap_quiet'] = False
        params['http_quiet'] = False

    if args.vrep:
        params['simulator'] = 'vrep'
    elif args.poppy_simu:
        params['simulator'] = 'poppy-simu'

    return params


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=('Poppy services launcher. Use it to quickly instantiate a ' +
                     'poppy creature with Snap!, an http server, or a remote robot.'),
        epilog="""
Examples:
* poppy-services --snap poppy-torso
* poppy-services --snap --vrep poppy-humanoid""",
        formatter_class=RawTextHelpFormatter)

    parser.add_argument('creature', type=str,
                        help='poppy creature name',
                        action='store', nargs='?',
                        choices=installed_poppy_creatures.keys())
    parser.add_argument('--vrep',
                        help='use a V-REP simulated Poppy Creature',
                        action='store_true')
    parser.add_argument('--poppy-simu',
                        help='use a Three.js visualization',
                        action='store_true')
    parser.add_argument('--snap',
                        help='start a Snap! robot server',
                        action='store_true')
    parser.add_argument('-nb', '--no-browser',
                        help='avoid automatic start of Snap! in web browser',
                        action='store_true')
    parser.add_argument('--http',
                        help='start a http robot server',
                        action='store_true')
    parser.add_argument('--remote',
                        help='start a remote robot server',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='start services with verbose mode. There is 3 debug levels, add as "v" as debug level you want',
                        action='count')
    parser.add_argument('-f', '--log-file',
                        help='Log filename',
                        action='store')

    args = parser.parse_args()

    # If no creature are specified and only one is installed
    # We use it as default.
    if not args.creature:
        if len(installed_poppy_creatures.keys()) > 1:
            parser.print_help()
            sys.exit(1)

        args.creature = installed_poppy_creatures.keys()[0]
        print('No creature specified, use {}'.format(args.creature))

    if args.log_file:
        fh = logging.FileHandler(args.log_file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logging.getLogger('').addHandler(fh)

    if args.verbose:
        args.snap_quiet = False
        args.http_quiet = False

        if args.verbose == 1:
            lvl = logging.WARNING
        elif args.verbose == 2:
            lvl = logging.INFO
        elif args.verbose > 2:
            lvl = logging.DEBUG

        ch = logging.FileHandler(args.log_file)
        ch.setLevel(lvl)
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        ch.setFormatter(formatter)
        logging.getLogger('').addHandler(ch)

    if not any([args.snap, args.http, args.remote, args.poppy_simu]):
        print('No service specified! See --help for details.')
        sys.exit(1)

    poppy = start_poppy_with_services(args)

    if args.snap and not args.no_browser:
        snap_url = 'http://snap.berkeley.edu/snapsource/snap.html'
        block_url = 'http://{}:{}/snap-blocks.xml'.format(find_local_ip(), poppy.snap.port)
        url = '{}#open:{}'.format(snap_url, block_url)

        for browser_name in ['chromium-browser', 'chromium', 'google-chrome',
                             'chrome', 'safari', 'midori', None]:
            try:
                browser = webbrowser.get(browser_name)
                browser.open(url, new=0, autoraise=True)
                break
            except:
                pass

    # Just run4ever (until Ctrl-c...)

    try:
        while(True):
            time.sleep(1000)
    except KeyboardInterrupt:
        print("Bye bye!")
