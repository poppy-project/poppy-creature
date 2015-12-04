#!/usr/bin/env python

import argparse
import webbrowser
import sys

from poppy.creatures import installed_poppy_creatures
from pypot.server.snap import find_local_ip


def main():

    deprecation_warning = 'poppy-snap is depreciated, it will be deleted in a next release. Use "poppy-services --snap" instead'
    parser = argparse.ArgumentParser(description='Snap! launcher for Poppy creatures', usage=deprecation_warning)
    parser.add_argument('creature', type=str,
                        help='poppy creature name',
                        action='store',  nargs='?',
                        choices=installed_poppy_creatures.keys())
    parser.add_argument('--vrep',
                        help='use a V-REP simulated Poppy Creature',
                        action='store_true')
    parser.add_argument('-nb', '--no-browser',
                        help='avoid automatic start of Snap! in web browser',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='display all Snap! server requests',
                        action='store_true')

    args = parser.parse_args()

    if not args.creature:
        if len(installed_poppy_creatures.keys()) == 1:
            args.creature = installed_poppy_creatures.keys()[0]
            print('No creature specified, use {}'.format(installed_poppy_creatures.keys()[0]))
        else:
            parser.print_help()
            sys.exit(0)

    poppy_args = {
        'use_snap': True
    }
    if args.verbose:
        poppy_args['snap_quiet'] = False
    if args.vrep:
        poppy_args['simulator'] = 'vrep'

    poppy = installed_poppy_creatures[args.creature](**poppy_args)

    snap_url = 'http://snap.berkeley.edu/snapsource/snap.html'
    block_url = 'http://{}:{}/snap-blocks.xml'.format(
        find_local_ip(),
        poppy.snap.port)

    url = '{}#open:{}'.format(snap_url, block_url)

    if args.no_browser:
        print('Snap is now running on: "{}"\n'.format(url))
    else:
        for bowser_name in ['chromium-browser', 'chromium', 'google-chrome', 'chrome',
                                                            'safari', 'midori', None]:
            try:
                browser = webbrowser.get(bowser_name)
                browser.open(url, new=0, autoraise=True)
                break
            except:
                pass
    print(deprecation_warning)

    poppy.snap.run()


if __name__ == '__main__':
    main()
