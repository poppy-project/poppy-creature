#!/usr/bin/env python

import socket
import argparse
import time

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
                        choices=installed_poppy_creatures.keys())
    parser.add_argument('--vrep', action='store_true')
    parser.add_argument('--snap', action='store_true')
    parser.add_argument('--http', action='store_true')
    parser.add_argument('--remote', action='store_true')
    args = parser.parse_args()

    poppy_args = {
        'use_snap': args.snap,
        'use_http': args.http,
        'use_remote': args.remote
    }
    if any([args.snap, args.http, args.remote]):
        if args.vrep:
            poppy_args['simulator'] = 'vrep'

        poppy = installed_poppy_creatures[args.creature](**poppy_args)
        AbstractPoppyCreature.start_background_services(poppy)

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
