#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function, division
import os
import sys
import subprocess
import platform
import socket
import urllib2
import time
import argparse
from argparse import RawTextHelpFormatter
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.WARNING)
logging.basicConfig()

zeroconf_logger = logging.getLogger('zeroconf')
zeroconf_logger.setLevel(logging.CRITICAL)

try:
    from zeroconf import ServiceBrowser, Zeroconf
except ImportError:
    print("You need to install python-zeroconf with `pip install zeroconf`")
    sys.exit(0)

global FOUND_HOSTS
FOUND_HOSTS = []

KEYS_SHORTCUT = {"mac_address": "Is a Raspberry Pi or a Odroid",
                 "home_page": "Has a Poppy robot home page",
                 "poppy_name": "Has a 'poppy' name",
                 "ip": "IP address",
                 "mac": "MAC address",
                 "hostname": "hostname",
                 "up": "online"}


def local_ip():
    return [l for l in ([ip for ip in
                         socket.gethostbyname_ex(socket.gethostname())[2]
                         if not ip.startswith('127.')][:1], [[(s.connect(('8.8.8.8',
                                                                          53)), s.getsockname()[0], s.close()) for s in
                                                              [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]])
            if l][0][0]


def ping(host, timeout=1):
    """
    Returns True if host responds to a ping request
    """

    EX_OK = getattr(os, "EX_OK", 1)
    # windows timeout is in miliseconds
    if platform.system().lower() == "windows":
        ping_params = ["-n 1", "-W %s" % (timeout * 1000), host]
    else:
        # POSIX ping timeout is in seconds and can't be bellow 1 (else it uses the default value)
        timeout = 1 if timeout < 1 else timeout
        ping_params = ["-c 1", "-W %s" % (timeout), host]

    p = subprocess.call(["ping"] + ping_params,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
    return p == EX_OK


def is_poppy_home_page(ip_adress, timeout=0.1):
    try:
        html = urllib2.urlopen('http://%s' % ip_adress, timeout=timeout).read()
        return "poppy" in html
    # except urllib2.URLError:
    #     return False
    except socket.timeout:
        return False
    except urllib2.URLError:
        return False


def is_poppy_board_mac(mac_address):

    if ':' in mac_address:
        splited_mac = mac_address.lower().split(':')
    elif '-' in mac_address:
        splited_mac = mac_address.lower().split('-')
    else:
        raise AttributeError("The mac address %s is not valid" % mac_address)
    # Look at http://hwaddress.com/?q=B827EB000000 for the mac adresses range
    rpi_prefix = ['b8', '27', 'eb']
    return rpi_prefix == splited_mac[:len(rpi_prefix)]


def service_browser_handler(zeroconf, service_type, name, state_change):
    found = {}
    hostname, other = name.split(' ')
    mac_address = other.split('.')[0].replace(']', '').replace('[', '')

    found["mac"] = mac_address
    found["hostname"] = hostname
    found["mac_address"] = is_poppy_board_mac(mac_address)
    found["poppy_name"] = "poppy" in hostname

    # If full option is activated or found a poppy board mac address
    if full or found["mac_address"] or found["poppy_name"]:
        info = zeroconf.get_service_info(service_type, name)
        try:
            ip = socket.inet_ntoa(info.address)
        except AttributeError:
            return
        logging.info('zeroconf find host %s at ip %s' % (hostname, ip))

    # We don't want to return our own computer
        if ip in local_ip() or hostname == socket.gethostname():
            return
        found["home_page"] = is_poppy_home_page(ip)
        if found["mac_address"] or found["poppy_name"] and not found["home_page"]:
            found["up"] = ping(ip)
        found["ip"] = ip
    FOUND_HOSTS.append(found)
    logger.info(found)


def print_output(found_list):
    poppy_list = []
    for robot in found_list:
        if True in ([v for v in robot.itervalues()]):
            poppy_list.append(robot)
            print("Found potential Poppy robot:")
            for key, value in robot.items():
                print("{} : {}".format(KEYS_SHORTCUT[key], value))
            print("\n")

    if len(poppy_list) == 0:
        print("No poppy robots founds ...")


def main():

    parser = argparse.ArgumentParser(
        description=('poppy-discover try to find poppy robots in the local network \n' +
                     'A computer is can be a poppy robot if any of these requirements is satisfied :\n' +
                     '* Is a Raspberry Pi or a Odroid\n' +
                     '* Has a Poppy robot home page\n' +
                     '* Its hostname contains "poppy"'
                     ),
        formatter_class=RawTextHelpFormatter)

    parser.add_argument('-v', '--verbose',
                        help='display logs informations',
                        action='store_true')
    parser.add_argument('-t', '--timeout',
                        help='Max time of browsing local network without result. Default is 3s',
                        action='store')
    parser.add_argument('--full',
                        help='Check poppy home page for every hosts',
                        action='store_true')
    args = parser.parse_args()
    timeout = int(args.timeout) if args.timeout else 3
    global full
    full = args.full

    if args.verbose:
        logger.setLevel(logging.INFO)
        logger.info("Info level activated")
        logger.info("timeout = %s" % timeout)

    zeroconf = Zeroconf()
    print("\nBrowsing Poppy robots, press Ctrl-C to exit...\n")
    browser = ServiceBrowser(zeroconf, "_workstation._tcp.local.", handlers=[service_browser_handler])

    try:
        while True:
            broken_loop = False
            for _ in range(3):
                results = len(FOUND_HOSTS)
                time.sleep(timeout / 3)
                if results != len(FOUND_HOSTS):
                    # logger.info("Loop breaks at %s with %s hosts founds" % (_, len(FOUND_HOSTS)))
                    broken_loop = True
                    break

            # Break while loop if no host have bee founds in {{ timeout }} seconds
            if not broken_loop:
                break
            print('%s hosts founds...' % len(FOUND_HOSTS))

    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
    print_output(FOUND_HOSTS)

if __name__ == '__main__':
    main()
