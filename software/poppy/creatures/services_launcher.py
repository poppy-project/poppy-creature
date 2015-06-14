#!/usr/bin/env python

import socket
import argparse
import time
import sys
import webbrowser

from poppy.creatures import installed_poppy_creatures
from .abstractcreature import AbstractPoppyCreature


def find_local_ip():
    # This is rather obscure...
    # go see here: http://stackoverflow.com/questions/166506/
    return [(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close())
            for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('creature', type=str,
                        help='poppy creature name',
                        action='store', nargs='?',
                        choices=installed_poppy_creatures.keys())
    parser.add_argument('--vrep',
                        help='use a V-REP simulated Poppy Creature',
                        action='store_true')
    parser.add_argument('--snap',
                        help='start a snap robot server',
                        action='store_true')
    parser.add_argument('--no-browser',
                        help='avoid automatic start of Snap! in web browser',
                        action='store_true')
    parser.add_argument('--http',
                        help='start a http robot server',
                        action='store_true')
    parser.add_argument('--remote',
                        help='start a remote robot server',
                        action='store_true')
    parser.add_argument('-v', '--verbose',
                        help='start services with verbose mode',
                        action='store_true')
    args = parser.parse_args()

    if not args.creature:
        parser.print_help()
        sys.exit(0)

    poppy_args = {
        'use_snap': args.snap,
        'use_http': args.http,
        'use_remote': args.remote
    }

    if args.verbose:
        poppy_args['snap_quiet'] = False
        poppy_args['http_quiet'] = False

    if any([args.snap, args.http, args.remote]):
        if args.vrep:
            poppy_args['simulator'] = 'vrep'

        poppy = installed_poppy_creatures[args.creature](**poppy_args)
        AbstractPoppyCreature.start_background_services(poppy)

        if args.snap:
            snap_url = 'http://snap.berkeley.edu/snapsource/snap.html'
            block_url = 'http://{}:{}/snap-blocks.xml'.format(find_local_ip(), poppy.snap.port)
            url = '{}#open:{}'.format(snap_url, block_url)

            print('Snap is now running on: "{}"\n'.format(url))
            if not args.no_browser:
                webbrowser.open(url, new=0, autoraise=True)

        print("Services started")
        try:
            while(True):
                time.sleep(1)
        except KeyboardInterrupt:
            print("Bye bye!")
    else:
        print("No service specified")
if __name__ == '__main__':
    main()
