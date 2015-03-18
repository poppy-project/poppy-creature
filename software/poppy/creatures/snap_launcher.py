#!/usr/bin/env python

import socket
import argparse
import webbrowser

from poppy.creatures import installed_poppy_creatures

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('creature', type=str,
                        choices=installed_poppy_creatures.keys())
    parser.add_argument('--vrep', action='store_true')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()

    poppy_args = {
        'use_snap': True
    }

    if args.vrep:
        poppy_args['simulator'] = 'vrep'

    poppy = installed_poppy_creatures[args.creature](**poppy_args)

    snap_url = 'http://snap.berkeley.edu/snapsource/snap.html'
    block_url = 'http://{}:{}/snap-blocks.xml'.format(
        socket.gethostbyname(socket.gethostname()),
        poppy.snap.port)

    url = '{}#open:{}'.format(snap_url, block_url)

    if args.no_browser:
        print('Snap is now running on: "{}"'.format(url))
    else:
        webbrowser.open(url, new=0, autoraise=True)

    poppy.snap.run()


if __name__ == '__main__':
    main()
