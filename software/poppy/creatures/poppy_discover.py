#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
import os
import sys
import subprocess
import platform
import socket
import urllib2
from time import sleep

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
                 "hostname": "hostname"}


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
    return p == os.EX_OK


def is_poppy_home_page(ip_adress, timeout=0.1):
    try:
        html = urllib2.urlopen('http://%s' % ip_adress, timeout=timeout).read()
        return "poppy" in html
    # except urllib2.URLError:
    #     return False
    except socket.timeout:
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
    hostname, other = name.split(' ')
    mac_address = other.split('.')[0].replace(']', '').replace('[', '')

    info = zeroconf.get_service_info(service_type, name)
    ip = socket.inet_ntoa(info.address)

    # We don't want to return our own computer
    if ip in local_ip() or hostname == socket.gethostname():
        return
    found = {}
    found["mac_address"] = is_poppy_board_mac(mac_address)
    found["home_page"] = is_poppy_home_page(ip)
    found["poppy_name"] = is_poppy_board_mac(mac_address)
    if found["mac_address"] or found["poppy_name"] and not found["home_page"]:
        found["up"] = ping(ip)
    found["ip"] = ip
    found["mac"] = mac_address
    found["hostname"] = hostname
    FOUND_HOSTS.append(found)


def print_output(found_list):
    poppy_list = []
    for robot in found_list:
        if True not in ([v for v in robot.itervalues()]):
            break
        else:
            poppy_list.append(robot)
            print("Found potential Poppy robot:")
            for key, value in robot.items():
                print("{} : {}".format(KEYS_SHORTCUT[key], value))
            print("\n")

    if len(poppy_list) == 0:
        print("No poppy robots founds ...")


def main():
    zeroconf = Zeroconf()
    print("\nBrowsing Poppy robots, press Ctrl-C to exit...\n")
    browser = ServiceBrowser(zeroconf, "_workstation._tcp.local.", handlers=[service_browser_handler])

    try:
        sleep(3)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
    print_output(FOUND_HOSTS)

if __name__ == '__main__':
    main()
