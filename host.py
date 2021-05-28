#!/usr/bin/env python

import argparse
import sys
import socket
import random
import struct
import re

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, hexdump
from scapy.all import Packet, hexdump
from scapy.all import Ether, IP, UDP, TCP
from scapy.all import Ether, StrFixedLenField, XByteField, IntField
from scapy.all import bind_layers
import readline
from myPPV import PPVheader

PPV_MIN = 1
PPV_MAX = 1024
PVV_CTV_DIFF = 200
BEHAVIOUR_DIFF = 100

class NumParseError(Exception):
    pass

class OpParseError(Exception):
    pass

class Token:
    def __init__(self,type,value = None):
        self.type = type
        self.value = value

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface


def generate_good(goods, ctv):
    results = [] 
    for g in goods:
        results.append((g, ctv, random.randint(ctv, PPV_MAX)))
    return results


def generate_neutral(neutrals, ctv):
    results = [] 
    for n in neutrals:
        results.append((n, ctv, random.randint(max(ctv - BEHAVIOUR_DIFF, PPV_MIN), ctv + BEHAVIOUR_DIFF)))
    return results

def generate_bad(bads, ctv):
    results = [] 
    for b in bads:
        results.append((b, ctv, random.randint(PPV_MIN, ctv + BEHAVIOUR_DIFF)))
    return results


def main():
    
    addr = socket.gethostbyname("10.0.2.2")
    iface = get_if()
    print "sending on interface {} to IP addr {}".format(iface, str(addr))

    #setting up the test generating
    random.seed(2)
    parser = argparse.ArgumentParser(description='Configure the number and the kind of data flows in the test run.')
    parser.add_argument('good', metavar='GOOD', type=int,
                        help='an integer that tells the program how many flows to create with good behaviour')
    parser.add_argument('neutral', metavar='NEUTRAL', type=int,
                        help='an integer that tells the program how many flows to create with neutral behaviour')
    parser.add_argument('bad', metavar='BAD', type=int,
                        help='an integer that tells the program how many flows to create with bad behaviour')

    args = parser.parse_args()

    flows = {}
    flows['good'] = list(range(1, args.good + 1))
    flows['neutral'] = list(range(args.good + 1, args.neutral + args.good + 1))
    flows['bad'] = list(range(args.neutral + args.good + 1, args.bad + args.neutral + args.good + 1))



    while True:
        try:


            packetList = []

            ctv = random.randint(PPV_MIN + PVV_CTV_DIFF, PPV_MAX - PVV_CTV_DIFF)
            packetList = packetList + generate_good(flows['good'], ctv)
            packetList = packetList + generate_neutral(flows['neutral'], ctv)
            packetList = packetList + generate_bad(flows['bad'], ctv)

            for packet in packetList:

                pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
                pkt = pkt / IP(dst=addr)

                pkt = pkt / PPVheader(
                                    Id=packet[0],
                                    CTV=packet[1],
                                    PPV=packet[2],
                                    Debug=0,
                                    FLAGGED=0)
                pkt = pkt/' '
                # pkt = pkt/ str('CTV=' + str(ctv) + ', PPV=' + str(ppv) + ', Id=' + str(id))
                # pkt = pkt/' '

                print "show1-----------------"
                pkt.show()
                print "-----------------"

                sendp(pkt, iface=iface, verbose=False)  

        except Exception as error:
            print "--------------------------tesa------------------"
            print error


if __name__ == '__main__':
    main()

