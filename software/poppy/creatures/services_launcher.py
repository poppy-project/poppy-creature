#!/usr/bin/env python

from __future__ import print_function
import time
import sys
import webbrowser
import logging
import argparse
from argparse import RawTextHelpFormatter

from pypot.server.snap import find_local_ip

from . import installed_poppy_creatures


def main():
    parser = argparse.ArgumentParser(
        description=('Poppy services launcher. Use it to quickly connect a ' +
                     'poppy creature with Snap!, http server, or a remote robot.'),
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

    if not args.creature:
        if len(installed_poppy_creatures.keys()) == 1:
            args.creature = installed_poppy_creatures.keys()[0]
            print('No creature specified, use {}'.format(installed_poppy_creatures.keys()[0]))
        else:
            parser.print_help()
            sys.exit(0)

    poppy_args = {
        'use_snap': args.snap,
        'use_http': args.http,
        'use_remote': args.remote
    }

    if args.log_file:
        fh = logging.FileHandler(args.log_file)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logging.getLogger('').addHandler(fh)

    if args.verbose:
        poppy_args['snap_quiet'] = False
        poppy_args['http_quiet'] = False
        console = logging.StreamHandler()
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

    if any([args.snap, args.http, args.remote, args.poppy_simu]):
        if args.vrep:
            poppy_args['simulator'] = 'vrep'
        elif args.poppy_simu:
            poppy_args['simulator'] = 'poppy-simu'

        poppy = installed_poppy_creatures[args.creature](**poppy_args)

        if args.snap:
            snap_url = 'http://snap.berkeley.edu/snapsource/snap.html'
            block_url = 'http://{}:{}/snap-blocks.xml'.format(find_local_ip(), poppy.snap.port)
            url = '{}#open:{}'.format(snap_url, block_url)

            if not args.no_browser:
                for bowser_name in ['chromium-browser', 'chromium', 'google-chrome',
                                    'chrome', 'safari', 'midori', None]:
                    try:
                        browser = webbrowser.get(bowser_name)
                        browser.open(url, new=0, autoraise=True)
                        break
                    except:
                        pass


        print("Services started")
        try:
            while(True):
                time.sleep(1)
        except KeyboardInterrupt:
            print("Bye bye!")
    else:
        print("No service specified. You want probably use snap")
if __name__ == '__main__':
    main()
